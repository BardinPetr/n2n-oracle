## Технические детали

### Образ с решением задачи

Решение задачи должно быть представленно в виде Docker образа `n2n-oracle`. Образ должен включать контракты, скрипт регистрации контрактов, оракула и т.д.

### Требования к контрактам (ABI):

#### Контракт управления набором валидаторов:
  - метод `addValidator(address newvalidator)` позволяет владельцу контракта добавлять нового валидатора.
  - метод `removeValidator(address validator)` позволяет владельцу контракта удалить одного из существующих валидаторов.
  - метод `changeThreshold(uint256 thresh)` позволяет владельцу контракта изменить пороговое значение необходимых подвтерждений от валидаторов, чтобы передача информации из одной блокчейн системы в другу считалась достоверной.
  - метод `getValidators()` позволяет получить текущий набор валидаторов.
  - метод `getThreshold()` позволяет получить текущее пороговое значение.

#### Контракт моста:
  - `changeValidatorSet(address newvalidatorset)` позволяет владельцу контракта изменить адрес контракта управления набором валидаторов.
  - `addLiquidity() payable` позволяет владельцу контракта на правой стороне увеличить количество токенов, послав их вместе с вызовом метода.
  - `updateLiquidityLimit(uint256 newlimit)` позволяет владельцу контракта на другой стороне синхронизировать лимит на передачу токенов с той стороны с количеством токенов добавленных в контракт моста.
  - `getLiquidityLimit()` позволяет получить какое максмиальное количество токенов может быть передано через мост.
  - `commit(address recipient, uint256 amount, bytes32 id)` позволяет валидатору моста подтвердить факт инициации передачи токенов через мост.
  - `() payable` позволяет пользователям блокчейн сети и другим контрактам инициировать передачу нативных токенов на другую сторону моста, просто отправив токены на адрес контракта моста. Испускает событие `bridgeActionInitiated(address recipient, uint256 amount)`.

### Скрипт регистрации контрактов

Скрипт, производящий регистрацию (deployment) контракта в блокчейн сети, опирается на следующие переменные окружения, заданные перед запуском скрипта:

```
# Приватный ключ, который используется для подписи транзакции, развертывающей
# контракты моста. На соответствующем приватному ключу счете должен быть
# достаточный баланс для исполнения операции развертывания
PRIVKEY=cafecafe...cafecafe

# URL, по которому будут доступны узлы, предоставляющий web3 сервис для
# взаимодействия с блокчейном с левой или правой стороны моста
LEFT_RPCURL=https://sokol.poa.network 
RIGHT_RPCURL=https://sokol.poa.network

# Цена за единицу газа, которая будет выставленна в транзакции, отправленные
# в блокчейн для левой или правой сторон моста
LEFT_GASPRICE=5000000000
RIGHT_GASPRICE=5000000000

# Адреса валидаторов моста
VALIDATORS=0xdeadbeaf...deadbeaf 0xbaddad...baddad

# Пороговое значение, определяющее какое количество валидаторов моста должны
# выслать подвтерждения, чтобы передача токенов через мост считалась достоверной
THRESHOLD=...
```

Запуск скрипта регистрации контрактов через контейнер:

```
$ docker run -ti --rm --env-file .env n2n-oracle /deployment/run.sh
```

### Оракул 

При запуске сервис оракула подразумевает в наличии следующих переменных окружения:

```
# Приватный ключ, соответствующий аккаунту валидатора моста
PRIVKEY=cafecafe...cafecafe

# URL, по которому будут доступны узлы, предоставляющий web3 сервис для
# взаимодействия с блокчейном с левой или правой стороны моста
LEFT_RPCURL=https://sokol.poa.network 
RIGHT_RPCURL=https://sokol.poa.network

# Цена за единицу газа, которая будет выставленна в транзакции, отправленные
# в блокчейн для левой или правой сторон моста
LEFT_GASPRICE=5000000000
RIGHT_GASPRICE=5000000000

# Адреса контрактов моста
LEFT_ADDRESS=0x
RIGHT_ADDRESS=0x

# Номера блоков, в котором были обработаны транзакции, регистрирующие контракты
# моста в блокчейн с левой и правой стороны моста
LEFT_START_BLOCK=X
RIGHT_START_BLOCK=X

# Путь до директории, в которой могут располагаться данные оракула, которые
# должны быть доступны после перезагрузки сервиса. Данная переменная должна
# использоваться в docker-compose.yml в секции, предоставляющей контейнеру
# получить доступ к файловой системе машины, на которой контейнер запускается.
# Пример, 
#    volumes:
#        - ${ORACLE_DATA}/db:/data
# где db -- директория на системе, запускающей контейнер
#     /data -- директория внутри контенера
ORACLE_DATA=/some/path
```

Оракул и все необходимые подсистемы должны автоматически стартануть после выполнения команды: 

```
$ docker-compose up -d
```

### Взаимодействие python c системой, выполняющей приемочное тестирование

Особенности системы запуска приемочного тестирования таковы, что следующих шаблон должен использоваться для подключения к RPC узлу:

```python
from web3 import Web3, HTTPProvider

w3 = Web3(HTTPProvider('http://some.rpc.url/'))

from web3.middleware import geth_poa_middleware

w3.middleware_onion.inject(geth_poa_middleware, layer=0)
```