# Environment

* CentOS7.x
    * 3.10.0-693.5.2.el7.x86_64
* Python 3.6.x

# About

## Analyze

各観測点のフルルート情報を取得し、それを元に以下のデータが書かれたファイル (以下 analyzedファイル) を出力します。

* 各 AS の広報するネットワークアドレス
* 各 AS の Neigbor の AS 番号

実行方法

```
bash analyze/analyze.sh
```

結果

```
less analyze/result.all
```

##  Sampling

analyzedファイルから、以下の AS を中心として n 個 AS を取り出します。

* Google (ASN 15169)
* Verizon (ASN 701)
* IIJ (ASN 2497)
* OCN (ASN 4713)

実行方法

```
python sampling_analyzedfile/sampling.py 100
```

結果

```
less sampling_analyzedfile/neighbors_100.txt
```

## Integration

analyzedファイルの ADDRESSES において、同ネットワークに属するアドレスを統合します。

実行方法

```
python integration_analyzedfile/integration_address.py neighbors_100.txt
```

結果

```
less integration_analyzedfile/addCombined.txt
```

## Create Heat Template

analyzedファイルを元に OpenStack Heat Template を作成します。

実行方法

* Network を作成するための HOT に必要なValuesファイル、Instance を作成するための HOT を生成

```
bash create_hot/create_hot.bash integration_analyzedfile/addCombined.txt
```

* HOT を OpenStack 上にデプロイ

```
bash create_hot/deployment-hot.bash create
```

* HOT を OpenStack 上から削除

```
bash create_hot/deployment-hot.bash delete
```
