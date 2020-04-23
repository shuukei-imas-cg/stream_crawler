# 指定したキーワードでツイートをStreaming APIで収集してDBに保存するスクリプト
第9回シンデレラガール総選挙 / ボイスアイドルオーディション を想定したもの。

Streaming APIを用い、デフォルトで #第9回シンデレラガール総選挙 と #ボイスアイドルオーディションのハッシュタグをもつツイートを監視・取得し、いわゆる「投票ツイート」と思われるものを対象に、タイトル(モバマス/デレステ)、投票モード(総選挙/ボイスアイドルオーディション)、投票先アイドル名などを判別したうえでDBに保存する。

Streaming APIは条件に合致するすべてのツイートを取得することを保証するものではないが、アイドル別のツイート数の傾向を統計的に捉えるには実用上問題ないと思われる。Search APIを用いる場合と違い、無料ユーザでもRate limitの制限がない利点がある。  
欠点としては、過去のツイートをまったく収集できないことで、これは、別途Search APIを用いて補う必要がある。


## 動作確認環境
- CentOS 6.9
- Python 2.7.11
- MySQL 5.7.28
	- MySQLについては、utf8mb4の文字コードが使えるバージョンであること


## 設定
1. MySQLで"senkyo" データベースを作成し、user: senkyo, password: senkyo のユーザを作成して当該データベースにパーミッションを与える
2. 初期テーブルを添付のsqlファイルを使って以下のように作成する。
~~~
mysql senkyo -u senkyo -p < sql/cg9th.sql
mysql senkyo -u senkyo -p < sql/idols.sql
~~~
3. Twitter APIキーを取得し、secret.pyに設定する。


## 起動
以下のように起動する。
~~~
python steram_crawler.py 
~~~

Twitterの都合で途中で止まることがあるので、supervisordなどを用いて常駐させるのがよい。


## SQLサンプル

### 指定した時間範囲に投票ツイートしたTwitterユニークユーザ数をアイドル別に集計(モード/タイトル別)
~~~
select idol, count(idol) as uu from (
  select
    user_id,count(user_id) as c,idol
  from cg9th
     where mode=1  # 0:cg9th 1:VA
     and title=1  # 0:mobamas 1:deresute
     and timestamp BETWEEN "2020-04-17 15:00:00" AND "2020-04-18 00:00:00"
  group by user_id, idol
  order by c desc
) as q group by idol order by uu desc
~~~

### VAについて、どのアイドルのTwitterユニークユーザが多いか(タイトル合算)
~~~
select q.idol_id, idols.name, count(q.idol_id) as uu from (
  select
    user_id,count(user_id) as c, idol_id, title
  from cg9th
     where mode=1
     and timestamp BETWEEN "2020-04-17 15:00:00" AND "2020-04-24 00:00:00"
  group by user_id, idol_id, title
  order by c desc
) as q, idols
where q.idol_id = idols.id
group by q.idol_id,idols.name order by uu desc
~~~

### VAで、あるアイドルに投票したTwitterユーザが、総選挙では誰に投票しているか
~~~
select idol,count(idol) as uu from (
    select user_id,count(user_id) as c,idol,title from cg9th where user_id in (
        select distinct user_id from cg9th where idol_id=226 and mode=1
    )
    and mode=0
    and timestamp BETWEEN "2020-04-17 15:00:00" AND "2020-04-24 00:00:00"
    group by user_id,idol,title order by c desc
) as q group by idol order by uu desc
~~~
