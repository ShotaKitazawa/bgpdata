# Environment

* CentOS7.x
    * 3.10.0-693.5.2.el7.x86_64
* Python 3.6.x
* OpenStack Pike

# About

## Preparation

* bgpdump のインストール

```
wget http://www.ris.ripe.net/source/bgpdump/libbgpdump-1.5.0.tgz
tar xvfz libbgpdump-1.5.0.tgz
cd libbgpdump-1.5.0
./configure
make
sudo cp bgpdump /usr/local/bin
```

* 必要なライブラリのインストール

```
pip install -r requirement.txt
```

* 事前に必要な OpenStack リソース
    * `external` network
        * 外部ネットワーク
    * `Ubuntu-Router` image
        * packer にて作成
    * `Ubuntu-Monitor` image
        * packer にて作成
    * `default` key-pair
    * `router` flavor
    * `monitor` flavor

## Analyze

各観測点のフルルート情報を取得し、それを元に以下のデータが書かれたファイル (以下 analyzedファイル) を出力します。

* 各 AS の広報するネットワークアドレス
* 各 AS の Neigbor の AS 番号

実行方法

```
bash analyze/analyze.bash
```

結果

```
less analyze/result.all
```

## Sampling

analyzedファイルから、以下の AS を中心として n 個 AS を取り出します。

* Google (ASN 15169)
* Verizon (ASN 701)
* IIJ (ASN 2497)
* OCN (ASN 4713)

実行方法

```
python sampling_analyzedfile/sampling_AS.py analyze/result.all 100
```

結果

```
less sampling_analyzedfile/neighbors_100.txt
```

## Create Heat Template

analyzedファイルを元に OpenStack Heat Template を作成します。

実行方法

* Network, Instance を作成するための HOT を生成

```
bash create_hot/create_hot.bash sampling_analyzedfile/neighbors_100.txt
```

結果

```
less create_hot/hot_instances.yaml
```
```
less create_hot/hot_networks.yaml
```

## Deploy Heat Template

OpenStack に HOT をデプロイします。`openstack` コマンドを使用するため、事前に rc ファイルを読み込んでください。

* HOT を OpenStack 上にデプロイ

```
bash deploy_hot/deploy_hot.bash create
```

* HOT を OpenStack 上から削除

```
bash deploy_hot/deploy_hot.bash delete
```
