from collections import OrderedDict
from django.template import loader
import os
import time
from django.conf import settings
from . models import Content, ContentCategory
from goods.models import GoodsCategory, GoodsChannel


def generate_static_index_file():
    """生成静态首页文件"""

    print('%s: generate_static_index_html' % time.ctime())
    # 设置频道,二级类别,三级类别的数据结构
    # categories = {
    #     # 1组
    #     1: {
    #         "channels": [{"key": "", "value": ""}, {}, {}],
    #         "second_cate": [
    #             {
    #                 "id": "",
    #                 "name": "",
    #                 "third_cate": [{"id": "", "name": ""}, {}, {}]
    #              },
    #             {},
    #         ]
    #     }
    #
    # }
    # 构建有序字典
    categories = OrderedDict()
    # 查询所有频道数据
    goods_channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in goods_channels:
        group_id = channel.group_id
        if group_id not in categories:
            categories[group_id] = {
                "channels": [],
                "second_cate": []
            }
        # 获取同一组的其他频道信息
        # 获取当前频道对应的一级类别
        cat1 = channel.category
        categories[group_id]['channels'].append(
            {
                "id": cat1.id,
                "name": cat1.name,
                "url": channel.url
            }
        )
        # 获取二级类别信息
        for cat2 in cat1.goodscategory_set.all():
            cat2.third_cate = []
            for cat3 in cat2.goodscategory_set.all():
                # 添加三级类别
                cat2.third_cate.append(cat3)
            categories[group_id]['second_cate'].append(cat2)
    # 广告内容
    # contents = {
    #    "key1": [{}, {}, {}]
    #    "key2": [{}, {}, {}]
    # }
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 渲染模板
    context = {
        "categories": categories,
        "contents": contents
    }

    template = loader.get_template('index.html')
    html_text = template.render(context)

    # 写入文件
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)
