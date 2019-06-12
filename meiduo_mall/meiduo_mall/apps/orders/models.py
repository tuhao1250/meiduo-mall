from django.db import models
from meiduo_mall.utils.models import BaseModel
# Create your models here.
from users.models import User, Address
from goods.models import SKU, Goods


class OrderInfo(BaseModel):
    """订单基本信息模型类"""

    PAY_METHOD_ENUM = {
        "CASH": 1,
        "ALIPAY": 2,
    }

    PAY_METHOD_CHOICES = (
        (1, "货到付款"),
        (2, "支付宝")
    )

    ORDER_STATUS_ENUM = {
        "UNPAID": 1,
        "UNSEND": 2,
        "UNRECEIVED": 3,
        "UNCOMMENT": 4,
        "FINISHED": 5,
        "CANDELED": 6,
    }

    ORDER_STATUS_CHOICES = (
        (1, "待支付"),
        (2, "代发货"),
        (3, "待收货"),
        (4, "待评价"),
        (5, "已完成"),
        (6, "已取消"),
    )

    oid = models.CharField(primary_key=True, max_length=64, verbose_name="订单编号")
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="下单用户")
    address = models.ForeignKey(Address, on_delete=models.PROTECT, verbose_name="用户收货地址")
    total_count = models.IntegerField(default=1, verbose_name="订单商品总数")
    total_amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="商品总金额")
    freight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="订单运费")
    pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES, default=1, verbose_name="支付方式")
    status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name="订单状态")

    class Meta:
        db_table = "tb_order_info"
        verbose_name = "订单信息表"
        verbose_name_plural = verbose_name


class OrderGoods(BaseModel):
    """订单商品表"""

    order = models.ForeignKey(OrderInfo, related_name="skus", on_delete=models.PROTECT, verbose_name="关联订单号")
    sku = models.ForeignKey(SKU, on_delete=models.PROTECT, verbose_name="订单商品")
    price = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="单价")
    count = models.IntegerField(default=1, verbose_name="数量")
    is_commented = models.BooleanField(default=False, verbose_name="是否评价完成")

    class Meta:
        db_table = 'tb_order_goods'
        verbose_name = "订单商品表"
        verbose_name_plural = verbose_name


class SKUComments(BaseModel):
    """商品SKU评论表"""

    SCORE_CHOICES = (
        (0, '0分'),
        (1, '20分'),
        (2, '40分'),
        (3, '60分'),
        (4, '80分'),
        (5, '100分'),
    )

    sku = models.ForeignKey(SKU, on_delete=models.PROTECT, related_name="skucomments", verbose_name="商品SKU")
    goods = models.ForeignKey(Goods, on_delete=models.PROTECT, related_name="goodscomments", verbose_name="商品SPU")
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="评价用户")
    comment = models.TextField(default="", verbose_name="评价内容")
    score = models.SmallIntegerField(choices=SCORE_CHOICES, default=5, verbose_name="满意度评分")
    is_anonymous = models.BooleanField(default=False, verbose_name="是否匿名评价")
    total_likes = models.IntegerField(default=0, verbose_name="点赞总数")
    total_comments = models.IntegerField(default=0, verbose_name="评论总数")

    class Meta:
        db_table = "tb_sku_comments"
        verbose_name = "SKU商品评价表"
        verbose_name_plural = verbose_name


class SubComments(BaseModel):
    """评论子表"""
    parent = models.ForeignKey(SKUComments, on_delete=models.PROTECT, related_name="subcomments", verbose_name="关联评论")
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="评论人")
    comment = models.TextField(default="", verbose_name="评论内容")

    class Meta:
        db_table = "tb_sub_comments"
        verbose_name = "评论子表"
        verbose_name_plural = verbose_name


class CommentLike(BaseModel):
    """评论点赞表"""
    comment_id = models.ForeignKey(SKUComments, on_delete=models.PROTECT, related_name="likes", verbose_name="关联评论")
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="点赞人")

    class Meta:
        db_table = "tb_comment_like"
        verbose_name = "评论点赞表"
        verbose_name_plural = verbose_name
