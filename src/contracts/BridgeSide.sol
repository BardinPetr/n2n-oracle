pragma solidity >=0.7.4 <=0.7.6;

import "./ValidatorSet.sol";

contract Victim {
    constructor () {}

    function sacrifice(address payable reciever) external payable {
        selfdestruct(reciever);
    }
}

contract DATAPACK { // used to incapsulate this data
    struct PA {
        uint256 confirmations;
        mapping(address => bool) is_confirmed_by;
    }
    mapping(bytes32 => PA) private _pending_actions;

    function isAlreadyConfirmed(bytes32 action_id, address confirmator) public view returns (bool) { // <---------- public
        if (_pending_actions[action_id].confirmations == type(uint256).max)
            return true;
        else
            return _pending_actions[action_id].is_confirmed_by[confirmator];
    }

    function confirmationsCount(bytes32 action_id) public view returns (uint256) { // <---------------------------- public
        return _pending_actions[action_id].confirmations;
    }

    function _confirmPendingAction(bytes32 action_id, address confirmator) internal {
        if (!isAlreadyConfirmed(action_id, confirmator))
        {
            PA storage context = _pending_actions[action_id];
            context.is_confirmed_by[confirmator] = true;
            context.confirmations += 1;
        }
        else
            revert("you cannot voice twice");
    }

    function _markCompleted(bytes32 action_id) internal {
        _pending_actions[action_id].confirmations = type(uint256).max; 
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
    bool private _robust_mode;

    struct Commit {
        uint256 r;
        uint256 s;
        uint8 v;
    }

    struct CommitsPool {
        address recipient;
        uint256 amount;
        Commit[] approvements;
    }

    mapping(bytes32 => CommitsPool) private commits;

    modifier only_for_owner() {
        require(msg.sender == _owner, "!owner");
        _;
    }

    modifier only_for_validators() {
        require(_validator_set.isValidator(msg.sender), "!validator");
        _;
    }

    modifier only_if_enabled() {
        require(_enabled, "bridge is disabled");
        _;
    }

// public methods

    constructor(address validator_set, bool side) {
        _owner = msg.sender;
        _validator_set = ValidatorSet(validator_set);
        _side = side;
        _enabled = true;
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

    function enableRobustMode() external only_for_owner {
        _robust_mode = true;
    }

    function stopOperations() external only_for_owner {
        _enabled = false;
    }

    function startOperations() external only_for_owner {
        _enabled = true;
    }

    function registerCommit(address recipient, uint256 amount, bytes32 id, uint256 r, uint256 s, uint8 v) external only_for_validators {
        require(!_side, "!!_side"); // only on the right side
        require(_robust_mode, "!_robust_mode");
    }

    function getTransferDetails(bytes32 id) external {
        require(!_side, "!!_side"); // only on the right side
    }

    function getCommit(bytes32 id, uint8 index) external returns (uint256 r, uint256 s, uint8 v) {
        require(!_side, "!!_side"); // only on the right side
    }

    function applyCommits(address recipient, uint256 amount, bytes32 id, uint256[] memory r, uint256[] memory s, uint8[] memory v) external {
        require(_side, "_side"); // only on the left side
    }

    function commit(address recipient, uint256 amount, bytes32 id) public only_for_validators only_if_enabled {
        require(!_robust_mode || !_side, "robust_enabled"); // block it only on left side if robust enabled
        _confirmPendingAction(id, msg.sender); // may revert here in such cases: (id marked as completed) or (msg.sender already vote)
        if (confirmationsCount(id) >= _validator_set.getThreshold())
        {
            require(address(this).balance >= amount, "!balance>=amount");
            if (!payable(recipient).send(amount))
                (new Victim()).sacrifice{value:amount}(payable(recipient));

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