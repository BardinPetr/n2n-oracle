pragma solidity >=0.7.4 <=0.7.6;

import "./ValidatorSet.sol";

contract FamilyWallet {
    event Received(address sender, uint256 value);
    address owner1;
    address owner2;
    
    constructor (address husband, address wife) {
        require(husband != wife, "the same");
        require(wife != address(0), "is zero");
        
        owner1 = husband;
        owner2 = wife;
    }
    
    function sendFunds(address payable receiver, uint256 value) external { 
        require(msg.sender == owner1 || msg.sender == owner2, "Not allowed");
        require(value <= address(this).balance, "not enough");
        receiver.transfer(value);
    }
    
    function receiveFunds() payable external {
        emit Received(msg.sender, msg.value);
    }
    
    receive () payable external {
        revert("Not supported");
    }
}

contract DATAPACK { // used to incapsulate this data
    struct PA {
        address[] confirmators;
        mapping(address => bool) is_confirmed_by;
    }
    mapping(bytes32 => PA) private _pending_actions;
    mapping(bytes32 => bool) private completed;

    function isAlreadyConfirmed(bytes32 action_id, address confirmator) public view returns (bool) { // <---------- public
        if (completed[action_id])
            return true;
        else
            return _pending_actions[action_id].is_confirmed_by[confirmator];
    }

    function confirmationsCount(bytes32 action_id) public view returns (uint256) { // <---------------------------- public
        if (completed[action_id])
            return type(uint256).max;
        else
            return _pending_actions[action_id].confirmators.length;
    }

    function _confirmPendingAction(bytes32 action_id, address confirmator) internal {
        if (!isAlreadyConfirmed(action_id, confirmator))
        {
            PA storage context = _pending_actions[action_id];
            context.is_confirmed_by[confirmator] = true;
            context.confirmators.push(confirmator);
        }
        else
            revert("you cannot voice twice");
    }

    function _markCompleted(bytes32 action_id) internal {
        completed[action_id] = true; 
    }
}

contract BridgeSide is DATAPACK {

    event bridgeActionInitiated(address recipient, uint256 amount);

    ValidatorSet private _validator_set;
    address private _owner;
    uint256 private _threshold;
    uint256 private _liquidity;
    uint256 private _opposite_side_balance;

    bool private _side;

    modifier only_for_owner() {
        require(msg.sender == _owner, "!owner");
        _;
    }

    modifier only_for_validators() {
        require(_validator_set.isValidator(msg.sender), "!validator");
        _;
    }

// public methods

    constructor(address validator_set, bool side) {
        _owner = msg.sender;
        _validator_set = ValidatorSet(validator_set);
        _side = side;
    }

    function changeValidatorSet(address addr) public only_for_owner {
        _validator_set = ValidatorSet(addr);
    }

    function addLiquidity() public payable only_for_owner {
        require(!_side, "!right_side"); // used only on right (_side == False) side, where some initiall ethers come here through this method
        require(msg.value > 0, "!value>0");
        _liquidity += msg.value;
    }
    
    function updateLiquidityLimit(uint256 newlimit) public only_for_owner {
        require(_side, "!left_side"); // used only on left (_side == True) side, where is no ethers initially
        _opposite_side_balance = newlimit;
        _liquidity = newlimit;
    }

    function getLiquidityLimit() public view returns (uint256) {
        return _liquidity;
    }

    function commit(address payable recipient, uint256 amount, bytes32 id) public only_for_validators {
        _confirmPendingAction(id, msg.sender); // may revert here in such cases: (id marked as completed) or (msg.sender already vote)
        if (confirmationsCount(id) >= _validator_set.getThreshold())
        {
            require(address(this).balance >= amount, "!balance>=amount");
            if (!recipient.send(amount))
            {
                FamilyWallet(recipient).receiveFunds{value:amount}();
            }

            _opposite_side_balance += amount;

            if (_side)
                _liquidity += amount;
            else
                _liquidity -= amount;
            
            _markCompleted(id);
        }
    }

    fallback() external payable {
        require(msg.value > 0, "!value>0");

        require(msg.value <= _opposite_side_balance, "!value<=osb");
        _opposite_side_balance -= msg.value;

        if (_side)
            _liquidity -= msg.value;
        else
            _liquidity += msg.value;

        emit bridgeActionInitiated(msg.sender, msg.value);
    }
}