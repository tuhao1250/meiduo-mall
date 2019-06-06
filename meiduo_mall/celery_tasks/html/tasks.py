from celery_tasks.main import celery_app
from django.template import loader
from django.conf import settings
import os

from goods.models import SKU
from goods.utils import get_categories


@celery_app.task(name='generate_static_sku_detail_html')
def generate_static_sku_detail_html(sku_id):
    """
    生成对应sku商品的详情页面
    :param sku_id: SKU商品的id
    :return:
    """

    # 生成商品分类数据
    categories = get_categories()

    # 获取SKU对象
    sku = SKU.objects.get(id=sku_id)
    # 获取sku对应的图片列表
    sku.images = sku.skuimage_set.all()


    # 面包屑导航
    spu = sku.goods
    spu.channel = spu.category1.goodschannel_set.all()[0]
    # 构建当前商品的规格键
    # sku_key = [规格1选项的值的id， 规格2参数id， 规格3参数id, ...]
    # 获取当前sku拥有的所有规格
    sku_specs = sku.skuspecification_set.all().order_by('spec_id')  # 注意要严格按照规格的id排序
    sku_key = []
    for spec in sku_specs:
        sku_key.append(spec.option.id)

    # 构建一个映射关系
    # 一个SKU对应的SPU所有的SKU_id以及对应的规格的选项的映射关系
    # spec_sku_map = {
    #     ('规格1对应的选项id', '规格2对应的选项id', '规格3对应的选项id',..): sku_id,
    #     ('规格1对应的选项id', '规格2对应的选项id', '规格3对应的选项id',..): sku_id,
    #     ('规格1对应的选项id', '规格2对应的选项id', '规格3对应的选项id',..): sku_id,
    #     ('规格1对应的选项id', '规格2对应的选项id', '规格3对应的选项id',..): sku_id,
    # }
    # 获取当前SKU商品对应SPU对应的所有SKU列表

    skus = spu.sku_set.all()
    spec_sku_map = {}
    # 生成映射关系字典
    for every_sku in skus:
        # 获取sku的规格对应选项id组成的字典
        sku_specs = every_sku.skuspecification_set.all().order_by('spec_id')
        # 因为元组不可以修改,所以需要先生成列表,再进行转换
        map_key = []
        for spec in sku_specs:
            map_key.append(spec.option.id)
        # 向map中添加键值对
        spec_sku_map[tuple(map_key)] = every_sku.id

    # 获取当前商品详情页需要展示的所有规格及每个规格可选的选项的信息
    # 考虑定义为如下结构:
    # specs_and_options = [
    #     {
    #         "name": "屏幕尺寸",
    #         "options": [
    #             {"value": "13.3寸", "sku_id": "xx"},
    #             {"value": "13.3寸", "sku_id": "xx"},
    #         ]
    #     },
    #     {
    #         "name": "颜色",
    #         "options": [
    #             {"value": "银色", "sku_id": "xx"},
    #             {"value": "灰色", "sku_id": "xx"},
    #         ]
    #     },
    #     ...
    # ]
    # 当前sku的规格及选项为sku_key
    # 获取spu的所有规格
    spu_specs = spu.goodsspecification_set.all().order_by('id')  # 一个包含了spu对应的所有规格的查询集
    specs_and_options = []
    if len(sku_key) < len(spu_specs):
        # 当前sku的规格信息不完整, 不再继续
        return
    for index, spec in enumerate(spu_specs):
        # print(spec)
        # 复制当前sku的规格键
        key = sku_key[:]
        # 该规格的对应的选项
        options = spec.specificationoption_set.all()
        for option in options:
            # print(option)
            key[index] = option.id
            option.sku_id = spec_sku_map.get(tuple(key))
        spec.options = options

        specs_and_options.append(spec)

    # 构建context
    context = {
        'categories': categories,  # 商品分类菜单
        'spu': spu,  # 商品对应的spu
        'specs_and_options': specs_and_options,  # sku对应的选项和规格的列表
        'sku': sku  # 本页面对应的sku
    }
    # 加载模板
    template = loader.get_template('detail.html')
    # 变量替换
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'goods/'+str(sku_id)+'.html')
    with open(file_path, 'w') as f:
        f.write(html_text)


# 生成静态列表页
@celery_app.task(name="genetate_static_list_html")
def generate_static_list_html():
    """
    生成静态list页面
    :return:
    """
    # 生成商品分类数据
    categories = get_categories()
    context = {
        'categories': categories
    }
    # 加载模板
    template = loader.get_template('list.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'list.html')
    with open(file_path, "w") as f:
        f.write(html_text)


# 生成静态搜索页
@celery_app.task(name="genetate_static_search_html")
def generate_static_search_html():
    """
    生成静态search页面
    :return:
    """
    # 生成商品分类数据
    categories = get_categories()
    context = {
        'categories': categories
    }
    # 加载模板
    template = loader.get_template('search.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'search.html')
    with open(file_path, "w") as f:
        f.write(html_text)




