from django.shortcuts import render

# Create your views here.
import json
import redis
from datetime import datetime
from random import shuffle
from operator import itemgetter
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.base import View
from django.conf import settings
from elasticsearch import Elasticsearch
from search.models import XianzhiArticleType, AnquankeArticleType, SihouArticleType

# 初始化一个ES连接,可指定多个主机(es支持分布式)
client = Elasticsearch(hosts=["127.0.0.1"])

redis_cli = redis.StrictRedis(host=settings.REDIS_HOST, password=settings.REDIS_PASS, charset='utf-8',
                              decode_responses=True)


class IndexView(View):
    def get(self, request):
        topn_search = redis_cli.zrevrangebyscore(
            "search_keywords_set", "+inf", "-inf", start=0, num=5)
        return render(request, "index.html", {"topn_search": topn_search})


class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s', '')
        re_datas = []
        if key_words:
            xianzhi = XianzhiArticleType.search()
            xianzhi = xianzhi.suggest('suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 'AUTO'  # 编辑距离
                },
                "size": 4
            })
            suggestions = xianzhi.execute_suggest()
            for match in suggestions.suggest[0].options:
                source = match._source
                re_datas.append(source['title'])

            anquanke = AnquankeArticleType.search()
            anquanke = anquanke.suggest('suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 'AUTO'  # 编辑距离
                },
                "size": 4
            })
            suggestions = anquanke.execute_suggest()
            for match in suggestions.suggest[0].options:
                source = match._source
                re_datas.append(source['title'])
            # 嘶吼提示
            sihou = SihouArticleType.search()
            sihou = sihou.suggest('suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 'AUTO'  # 编辑距离
                },
                "size": 4
            })
            suggestions = sihou.execute_suggest()
            for match in suggestions.suggest[0].options:
                source = match._source
                re_datas.append(source['title'])
        shuffle(re_datas)
        return HttpResponse(json.dumps(re_datas), content_type='application/json')


class SearchView(View):
    def get(self, request):
        key_words = request.GET.get('q', '')

        # 热门搜索
        # 将关键词加入redis中
        redis_cli.zincrby("search_keywords_set", 1, key_words)
        topn_search = redis_cli.zrevrangebyscore(
            "search_keywords_set", "+inf", "-inf", start=0, num=5)

        page = request.GET.get('p', '1')
        try:
            page = int(page)
        except:
            page = 1

        article_count = [redis_cli.get("xianzhi_count"), redis_cli.get("anquanke_count"), redis_cli.get("sihou_count")]

        start_time = datetime.now()
        xz_response = client.search(
            index="xianzhi",
            body={
                "query": {
                    "multi_match": {
                        "query": key_words,
                        "fields": ["tags", "title", "content"]
                    }
                },
                "from": (page - 1) * 5,
                "size": 5,
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "title": {},
                        "content": {},
                        "tags": {}
                    }
                }
            }
        )
        aqk_response = client.search(
            index="anquanke",
            body={
                "query": {
                    "multi_match": {
                        "query": key_words,
                        "fields": ["tags", "title", "content"]
                    }
                },
                "from": (page - 1) * 5,
                "size": 5,
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "title": {},
                        "content": {},
                        "tags": {}
                    }
                }
            }
        )
        sh_response = client.search(
            index="sihou",
            body={
                "query": {
                    "multi_match": {
                        "query": key_words,
                        "fields": ["tags", "title", "content"]
                    }
                },
                "from": (page - 1) * 5,
                "size": 5,
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "title": {},
                        "content": {},
                        "tags": {}
                    }
                }
            }
        )
        end_time = datetime.now()
        last_seconds = (end_time - start_time).total_seconds()
        total_nums = xz_response["hits"]["total"] + aqk_response["hits"]["total"] + sh_response["hits"]["total"]
        if (page % 15) > 0:
            page_nums = int(total_nums / 15 + 1)
        else:
            page_nums = int(total_nums / 15)

        hit_list = []
        for hit in xz_response["hits"]["hits"]:
            hit_dict = {}
            if 'highlight' in hit and 'title' in hit['highlight']:
                hit_dict['title'] = ''.join(hit['highlight']['title'])
            else:
                hit_dict['title'] = hit['_source']['title']
            if 'highlight' in hit and 'tags' in hit['highlight']:
                hit_dict['tags'] = ''.join(hit['highlight']['tags'])
            else:
                hit_dict['tags'] = hit['_source']['tags']
            if 'highlight' in hit and 'content' in hit['highlight']:
                hit_dict['content'] = ''.join(hit['highlight']['content'][:500])
            else:
                hit_dict['content'] = hit['_source']['content'][:500]

            hit_dict['create_date'] = str(hit['_source']['create_date']).replace('T', ' ')
            hit_dict['url'] = hit['_source']['url']
            hit_dict['author'] = hit['_source']['author']
            hit_dict['view_count'] = hit['_source']['view_count']
            hit_dict['score'] = hit['_score']
            hit_dict['source_site'] = '先知社区'
            hit_list.append(hit_dict)

        for hit in aqk_response["hits"]["hits"]:
            hit_dict = {}
            if 'highlight' in hit and 'title' in hit['highlight']:
                hit_dict['title'] = ''.join(hit['highlight']['title'])
            else:
                hit_dict['title'] = hit['_source']['title']
            if 'highlight' in hit and 'tags' in hit['highlight']:
                hit_dict['tags'] = ''.join(hit['highlight']['tags'])
            else:
                hit_dict['tags'] = hit['_source']['tags']
            if 'highlight' in hit and 'content' in hit['highlight']:
                hit_dict['content'] = ''.join(hit['highlight']['content'][:500])
            else:
                hit_dict['content'] = hit['_source']['content'][:500]

            hit_dict['create_date'] = str(hit['_source']['create_date']).replace('T', ' ')
            hit_dict['url'] = hit['_source']['url']
            hit_dict['author'] = hit['_source']['author']
            hit_dict['view_count'] = hit['_source']['view_count']
            hit_dict['score'] = hit['_score']
            hit_dict['source_site'] = '安全客'
            hit_list.append(hit_dict)

        for hit in sh_response["hits"]["hits"]:
            hit_dict = {}
            if 'highlight' in hit and 'title' in hit['highlight']:
                hit_dict['title'] = ''.join(hit['highlight']['title'])
            else:
                hit_dict['title'] = hit['_source']['title']
            if 'highlight' in hit and 'tags' in hit['highlight']:
                hit_dict['tags'] = ''.join(hit['highlight']['tags'])
            else:
                hit_dict['tags'] = hit['_source']['tags']
            if 'highlight' in hit and 'content' in hit['highlight']:
                hit_dict['content'] = ''.join(hit['highlight']['content'][:500])
            else:
                hit_dict['content'] = hit['_source']['content'][:500]

            hit_dict['create_date'] = str(hit['_source']['create_date']).replace('T', ' ')
            hit_dict['url'] = hit['_source']['url']
            hit_dict['author'] = hit['_source']['author']
            hit_dict['view_count'] = hit['_source']['view_count']
            hit_dict['score'] = hit['_score']
            hit_dict['source_site'] = '嘶吼'
            hit_list.append(hit_dict)
        # 按score的降序进行排列
        hit_list = sorted(hit_list, key=itemgetter('score'), reverse=True)
        return render(request, 'result.html', {'all_hits': hit_list,
                                               'key_words': key_words,
                                               'total_nums': total_nums,
                                               'last_seconds': last_seconds,
                                               'article_count': article_count,
                                               'page': page,
                                               'page_nums': page_nums,
                                               'topn_search': topn_search})
