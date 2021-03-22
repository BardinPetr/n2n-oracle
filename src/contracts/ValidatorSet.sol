pragma solidity >=0.7.4 <=0.7.6;

contract ValidatorsPool {
    address[] private _validators;
    mapping(address => bool) private _is_validator;

    function getValidators() public view returns (address[] memory) { // <--------------------------------------------- public
        return _validators;
    }

    function isValidator(address addr) public view returns (bool) { // <----------------------------------------------- public
        return _is_validator[addr];
    }

    function _addValidator(address addr) internal {
        if (!_is_validator[addr])
        {
            _is_validator[addr] = true;
            _validators.push(addr);
        }
        else
            revert("!!validator");
    }

    function _removeValidator(address addr) internal {
        if (_is_validator[addr])
        {
            _is_validator[addr] = false;
            for (uint256 i = 0; i < _validators.length; i++)
            {
                if (_validators[i] == addr)
                {
                    _validators[i] = _validators[_validators.length - 1];
                    _validators.pop();
                    break;
                }
            }
        }
        else
            revert("!validator");
    }
}

contract ValidatorSet is ValidatorsPool {

    address private _owner;
    uint256 private _threshold;

    modifier only_for_owner() {
        require(msg.sender == _owner, "!owner");

        _;
    }

// public methods

    constructor(address[] memory validators, uint256 threshold) {
        _owner = msg.sender;
        for (uint256 i = 0; i < validators.length; i++) {
            _addValidator(validators[i]);
        }
        changeThreshold(threshold);
    }

    function addValidator(address addr) public only_for_owner {
        _addValidator(addr);
    }

    function removeValidator(address addr) public only_for_owner {
        require(getValidators().length > 2, "!validators>2");
        _removeValidator(addr);
    }

    function changeThreshold(uint256 th) public only_for_owner {
        require(th > 0, "!th>0");
        require(th <= getValidators().length, "!th<=validators.length");
        _threshold = th;
    }

    function getThreshold() public view returns (uint256) {
        return _threshold;
    }
}