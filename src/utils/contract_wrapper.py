from .tools import to_address


class ContractWrapper:
    def __init__(self, w3, gas_price, user_pk, **kwargs):
        """
        Методы автоматически определяются как call или buildTransaction
        > методы определенные как call возвращают результат функции
        > методы определенные как bT возвращают рецепт отправленной транзакции

        Args:
            w3 (Web3): экземпляр web3 для общения с блокчеином.
            **kwargs (type): парамтры как для eth.contract().
        """
        user_acc = to_address(user_pk)
        contract = w3.eth.contract(**kwargs)
        fallback_gp = 10000

        # setup events
        self.events = contract.events

        # setup constructor
        def construct(*args, **kwargs):
            tx = contract.constructor(*args, **kwargs).buildTransaction({
                'gasPrice': gas_price,
                'nonce': w3.eth.getTransactionCount(user_acc)
            })

            signed = w3.eth.account.signTransaction(tx, private_key=user_pk)
            tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)

            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            return tx_receipt

        setattr(self, 'constructor', construct)

        # setup contract methods
        for elem in kwargs['abi']:
            if 'name' in elem:
                try:
                    # choose call or buildTransaction
                    if elem['stateMutability'] in ['view', 'pure']:
                        def funct(name):
                            def func(*args, **kwargs):
                                return getattr(contract.functions, name)(*args, **kwargs).call()

                            return func
                    else:
                        def funct(name):
                            def func(*args, **kwargs):
                                value = 0 if 'value' not in kwargs.keys() else kwargs.pop('value')

                                tx = {
                                    'from': user_acc,
                                    'to': contract.address,
                                    'value': value,
                                    'gasPrice': gas_price,
                                    'nonce': w3.eth.getTransactionCount(user_acc),
                                    'data': contract.encodeABI(fn_name=name, args=args, kwargs=kwargs)
                                }

                                results = None
                                try:
                                    # this line will throw detailed exception with revert reason
                                    # in case of fault (an instance of ContractLogicError)
                                    results = w3.eth.call(tx)
                                except ValueError as ex:
                                    if 'insufficient' in ex.args[0]['message']:
                                        tx['gasPrice'] = fallback_gp
                                        results = w3.eth.call(tx)
                                        
                                tx['gas'] = w3.eth.estimateGas(tx)

                                signed = w3.eth.account.signTransaction(tx, private_key=user_pk)
                                tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
                                tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

                                return tx_receipt, results

                            return func
                    setattr(self, elem['name'], funct(elem['name']))
                except KeyError:
                    pass
