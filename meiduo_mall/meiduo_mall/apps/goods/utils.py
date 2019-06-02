from collections import OrderedDict

from goods.models import GoodsChannel


def get_categories():
    """
    获取商城商品分类菜单
    :return: 菜单字典
    """
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
    return categories
