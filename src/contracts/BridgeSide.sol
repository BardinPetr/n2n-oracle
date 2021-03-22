pragma solidity >=0.7.4 <=0.7.6;

import "./ValidatorSet.sol";

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

    modifier only_for_owner() {
        require(msg.sender == _owner, "!owner");
        _;
    }

    modifier only_for_validators() {
        require(_validator_set.isValidator(msg.sender), "!validator");
        _;
    }

// public methods

    constructor(address validator_set) {
        _owner = msg.sender;
        _validator_set = ValidatorSet(validator_set);
    }

    function changeValidatorSet(address addr) public only_for_owner {
        _validator_set = ValidatorSet(addr);
    }

    function addLiquidity() public payable only_for_owner {
        require(msg.value > 0, "!value>0");
    }

    function updateLiquidityLimit(uint256 newlimit) public only_for_owner {
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
            require(recipient.send(amount), "!send");
            _markCompleted(id);
        }
    }

    fallback() external payable {
        require(msg.value > 0, "!value>0");
        require(msg.value <= _liquidity, "!value<=liquidity");
        _liquidity -= msg.value;
        emit bridgeActionInitiated(msg.sender, msg.value);
    }
}