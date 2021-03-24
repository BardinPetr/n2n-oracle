pragma solidity >=0.7.4 <=0.7.6;

import "./ValidatorSet.sol";

contract Victim {
    constructor () {}

    function sacrifice(address reciever) external payable {
        selfdestruct(payable(reciever));
    }
}

contract DATAPACK {// used to incapsulate this data
    struct PA {
        uint256 confirmations;
        mapping(address => bool) is_confirmed_by;
    }

    mapping(bytes32 => PA) private _pending_actions;

    function isAlreadyConfirmed(bytes32 action_id, address confirmator) public view returns (bool) {// <---------- public
        if (_pending_actions[action_id].confirmations == type(uint256).max)
            return true;
        else
            return _pending_actions[action_id].is_confirmed_by[confirmator];
    }

    function confirmationsCount(bytes32 action_id) public view returns (uint256) {// <---------------------------- public
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

    event commitsCollected(bytes32 id, uint8 commits);
    event bridgeActionInitiated(address recipient, uint256 amount);

    bytes25 constant EIP191_VERSION_E_HEADER = "Ethereum Signed Message:\n";

    ValidatorSet private _validator_set;
    address private _owner;
    uint256 private _threshold;
    uint256 private _liquidity;
    uint256 private _opposite_side_balance;

    bool private _side;
    bool private _robust_mode;
    bool private _enabled;

    uint256 private _min_per_tx = 0;
    uint256 private _max_per_tx = type(uint256).max;

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

    mapping(bytes32 => CommitsPool) private commits; // id -> CommitsPool

    modifier only_for_owner() {
        require(msg.sender == _owner, "!owner");
        _;
    }

    modifier only_for_validators() {
        require(_validator_set.isValidator(msg.sender), "!validator");
        _;
    }

    function hashEIP191versionE(bytes memory _message) internal view returns (bytes32 result) {
        uint256 length = _message.length;
        require(length > 0, "Empty message not allowed for version E");

        // Compute text-encoded length of message
        uint256 digits = 0;
        while (length != 0) {
            digits++;
            length /= 10;
        }
        bytes memory lengthAsText = new bytes(digits);
        length = _message.length;
        uint256 index = digits - 1;
        while (length != 0) {
            lengthAsText[index--] = byte(uint8(48 + length % 10));
            length /= 10;
        }
        return keccak256(abi.encodePacked(byte(0x19), EIP191_VERSION_E_HEADER, lengthAsText, _message));
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

    function setMinPerTx(uint256 _min) public only_for_owner {
        require(_min < _max_per_tx, "min>max");
        _min_per_tx = _min;
    }

    function setMaxPerTx(uint256 _max) public only_for_owner {
        require(_max > _min_per_tx, "min>max");
        _max_per_tx = _max;
    }

    function _checkAmount(uint256 val) internal {
        require(val > _min_per_tx, "too_low_value");
        require(val < _max_per_tx, "too_high_value");
    }

    function changeValidatorSet(address addr) public only_for_owner {
        _validator_set = ValidatorSet(addr);
    }

    function addLiquidity() public payable only_for_owner {
        require(!_side, "!right_side");
        // used only on right (_side == False) side, where some initiall ethers come here through this method
        require(msg.value > 0, "!value>0");
        _liquidity += msg.value;
    }

    function updateLiquidityLimit(uint256 newlimit) public only_for_owner {
        require(_side, "!left_side");
        // used only on left (_side == True) side, where is no ethers initially
        _opposite_side_balance = newlimit;
        _liquidity = newlimit;
    }

    function getLiquidityLimit() public view returns (uint256) {
        return _liquidity;
    }

    function enableRobustMode() external only_for_owner {
        _robust_mode = true;
    }

    function getRobustModeMessage(address recipient, uint256 amount, bytes32 id) public returns (bytes memory) {
        return abi.encodePacked(recipient, amount, id);
    }

    function stopOperations() external only_for_owner {
        _enabled = false;
    }

    function startOperations() external only_for_owner {
        _enabled = true;
    }

    function _getMsgHash(address recipient, uint256 amount, bytes32 id) internal returns (bytes32) {
        return hashEIP191versionE(getRobustModeMessage(recipient, amount, id));
    }

    function _recover(bytes32 msghash, uint256 r, uint256 s, uint8 v) internal returns (address) {
        return ecrecover(msghash, v, bytes32(r), bytes32(s));
    }

    function _recover(address recipient, uint256 amount, bytes32 id, uint256 r, uint256 s, uint8 v) internal returns (address){
        return _recover(_getMsgHash(recipient, amount, id), r, s, v);
    }

    function registerCommit(address recipient, uint256 amount, bytes32 id, uint256 r, uint256 s, uint8 v) external only_for_validators {
        require(!_side, "!!_side");
        // only on the right side
        require(_robust_mode, "!_robust_mode");
        require(commits[id].approvements.length < _validator_set.getThreshold(), "already_approved");

        address recovered = _recover(recipient, amount, id, r, s, v);
        require(_validator_set.isValidator(recovered), "no_a_validator_signature");

        commits[id].recipient = recipient;
        commits[id].amount = amount;
        commits[id].approvements.push(Commit(r, s, v));

        if (commits[id].approvements.length >= _validator_set.getThreshold())
            emit commitsCollected(id, uint8(commits[id].approvements.length));
    }

    function getTransferDetails(bytes32 id) external returns (address recipient, uint256 amount) {
        require(!_side, "!!_side");
        // only on the right side
        return (commits[id].recipient, commits[id].amount);
    }

    function getCommit(bytes32 id, uint8 index) external returns (uint256 r, uint256 s, uint8 v) {
        require(!_side, "!!_side");
        // only on the right side
        Commit storage tmp = commits[id].approvements[index];
        return (tmp.r, tmp.s, tmp.v);
    }

    function applyCommits(address recipient, uint256 amount, bytes32 id, uint256[] memory r, uint256[] memory s, uint8[] memory v) external {
        require(_side, "_side");
        // only on the left side
        bytes32 msghash = _getMsgHash(recipient, amount, id);
        uint confirmations = 0;
        for (uint i = 0; i < r.length; i++) {
            address recovered = _recover(msghash, r[i], s[i], v[i]);
            require(recovered != address(0x0), "!apply1");
            if (_validator_set.isValidator(recovered))
                confirmations += 1;
        }

        require(confirmations >= _validator_set.getThreshold(), "not_enough_commits");
        require(address(this).balance >= amount, "!balance>=amount");
        if (!payable(recipient).send(amount))
            (new Victim()).sacrifice{value:amount}(recipient);
    }

    function commit(address recipient, uint256 amount, bytes32 id) public only_for_validators {
        require(!_robust_mode || !_side, "robust_enabled");
        // block it only on left side if robust enabled
        _checkAmount(amount);
        _confirmPendingAction(id, msg.sender);
        // may revert here in such cases: (id marked as completed) or (msg.sender already vote)
        if (confirmationsCount(id) >= _validator_set.getThreshold())
        {
            require(address(this).balance >= amount, "!balance>=amount");
            if (!payable(recipient).send(amount))
                (new Victim()).sacrifice{value : amount}(recipient);

            _opposite_side_balance += amount;

            if (_side)
                _liquidity += amount;
            else
                _liquidity -= amount;

            _markCompleted(id);
        }
    }

fallback() external payable only_if_enabled {
_checkAmount(msg.value);

require(msg.value <= _opposite_side_balance, "!value<=osb");
_opposite_side_balance -= msg.value;

if (_side)
_liquidity -= msg.value;
else
_liquidity += msg.value;

emit bridgeActionInitiated(msg.sender, msg.value);
}
}