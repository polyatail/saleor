import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import HStoreField
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import F, Max, Q
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.text import slugify
from django.utils.translation import pgettext_lazy
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from satchless.item import Item, ItemRange
from text_unidecode import unidecode
from versatileimagefield.fields import PPOIField, VersatileImageField



class Category(MPTTModel):
    name = models.CharField(
        pgettext_lazy('Category field', 'name'), max_length=128)
    slug = models.SlugField(
        pgettext_lazy('Category field', 'slug'), max_length=50)
    description = models.TextField(
        pgettext_lazy('Category field', 'message to users'), blank=True)
    prices = models.BooleanField(
        pgettext_lazy('Category field', 'prices enabled'), default=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children',
        verbose_name=pgettext_lazy('Category field', 'parent'),
        on_delete=models.CASCADE)

    objects = models.Manager()
    tree = TreeManager()

    class Meta:
        app_label = 'product'
        permissions = (
            ('view_category',
             pgettext_lazy('Permission description', 'Can view categories')),
            ('edit_category',
             pgettext_lazy('Permission description', 'Can edit categories')))

    def __str__(self):
        return self.name

    def get_full_path(self, ancestors=None):
        if not self.parent_id:
            return self.slug
        if not ancestors:
            ancestors = self.get_ancestors()
        nodes = [node for node in ancestors] + [self]
        return '/'.join([node.slug for node in nodes])

class UserField(models.Model):
    name = models.CharField("Name", max_length=128)
    description = models.TextField("Description", blank=True)
    company = models.ForeignKey(Category, on_delete=models.CASCADE)


class ProductClass(models.Model):
    name = models.CharField(
        pgettext_lazy('Product class field', 'name'), max_length=128)
    has_variants = models.BooleanField(
        pgettext_lazy('Product class field', 'has variants'), default=True)
    product_attributes = models.ManyToManyField(
        'ProductAttribute', related_name='products_class', blank=True,
        verbose_name=pgettext_lazy('Product class field',
                                   'product attributes'))
    variant_attributes = models.ManyToManyField(
        'ProductAttribute', related_name='product_variants_class', blank=True,
        verbose_name=pgettext_lazy(
            'Product class field', 'variant attributes'))

    class Meta:
        app_label = 'product'

    def __str__(self):
        return self.name

    def __repr__(self):
        class_ = type(self)
        return '<%s.%s(pk=%r, name=%r)>' % (
            class_.__module__, class_.__name__, self.pk, self.name)


class ProductManager(models.Manager):
    def get_available_products(self):
        return self.get_queryset().filter(is_published=True)


class Product(models.Model, ItemRange):
    product_class = models.ForeignKey(
        ProductClass, related_name='products',
        verbose_name=pgettext_lazy('Product field', 'product class'),
        on_delete=models.CASCADE)
    name = models.CharField(
        pgettext_lazy('Product field', 'name'), max_length=128)
    price = models.DecimalField('Price', max_digits=6, decimal_places=2)
#    description = models.TextField(
#        verbose_name=pgettext_lazy('Product field', 'description'), blank=True)
    categories = models.ManyToManyField(
        Category, verbose_name=pgettext_lazy('Product field', 'companies'),
        related_name='products')
    is_published = models.BooleanField(
        pgettext_lazy('Product field', 'is published'), default=True)
    attributes = HStoreField(
        pgettext_lazy('Product field', 'attributes'), default={})
    updated_at = models.DateTimeField(
        pgettext_lazy('Product field', 'updated at'), auto_now=True, null=True)

    objects = ProductManager()

    class Meta:
        app_label = 'product'
        permissions = (
            ('view_product',
             pgettext_lazy('Permission description', 'Can view products')),
            ('edit_product',
             pgettext_lazy('Permission description', 'Can edit products')),
            ('view_properties',
             pgettext_lazy(
                 'Permission description', 'Can view product properties')),
            ('edit_properties',
             pgettext_lazy(
                 'Permission description', 'Can edit product properties')))

    def __iter__(self):
        if not hasattr(self, '__variants'):
            setattr(self, '__variants', self.variants.all())
        return iter(getattr(self, '__variants'))

    def __repr__(self):
        class_ = type(self)
        return '<%s.%s(pk=%r, name=%r)>' % (
            class_.__module__, class_.__name__, self.pk, self.name)

    def __str__(self):
        return self.name

    def get_slug(self):
        return slugify(smart_text(unidecode(self.name)))

    def get_first_category(self):
        for category in self.categories.all():
            return category
        return None

    def is_available(self):
        return True

    def get_first_image(self):
        first_image = self.images.first()

        if first_image:
            return first_image.image
        return None

    def get_attribute(self, pk):
        return self.attributes.get(smart_text(pk))

    def set_attribute(self, pk, value_pk):
        self.attributes[smart_text(pk)] = smart_text(value_pk)


class ProductVariant(models.Model, Item):
    sku = models.CharField(
        pgettext_lazy('Product variant field', 'SKU'), max_length=32,
        unique=True)
    name = models.CharField(
        pgettext_lazy('Product variant field', 'variant name'), max_length=100,
        blank=True)
    product = models.ForeignKey(
        Product, related_name='variants', on_delete=models.CASCADE)
    attributes = HStoreField(
        pgettext_lazy('Product variant field', 'attributes'), default={})
    images = models.ManyToManyField(
        'ProductImage', through='VariantImage',
        verbose_name=pgettext_lazy('Product variant field', 'images'))

    class Meta:
        app_label = 'product'

    def __str__(self):
        return self.name or self.display_variant()

    def check_quantity(self, quantity):
        pass

    def as_data(self):
        return {
            'product_name': str(self),
            'product_id': self.product.pk,
            'variant_id': self.pk,}

    def get_attribute(self, pk):
        return self.attributes.get(smart_text(pk))

    def set_attribute(self, pk, value_pk):
        self.attributes[smart_text(pk)] = smart_text(value_pk)

    def display_variant(self, attributes=None):
        if attributes is None:
            attributes = self.product.product_class.variant_attributes.all()
        from .utils import get_attributes_display_map
        values = get_attributes_display_map(self, attributes)
        if values:
            return ', '.join(
                ['%s: %s' % (smart_text(attributes.get(id=int(key))),
                             smart_text(value))
                 for (key, value) in values.items()])
        else:
            return smart_text(self.sku)

    def display_product(self):
        return '%s (%s)' % (smart_text(self.product), smart_text(self))

    def get_first_image(self):
        return self.product.get_first_image()


class ProductAttribute(models.Model):
    slug = models.SlugField(
        pgettext_lazy('Product attribute field', 'internal name'),
        max_length=50, unique=True)
    name = models.CharField(
        pgettext_lazy('Product attribute field', 'display name'),
        max_length=100)

    class Meta:
        ordering = ('slug', )

    def __str__(self):
        return self.name

    def get_formfield_name(self):
        return slugify('attribute-%s' % self.slug, allow_unicode=True)

    def has_values(self):
        return self.values.exists()


class AttributeChoiceValue(models.Model):
    name = models.CharField(
        pgettext_lazy('Attribute choice value field', 'display name'),
        max_length=100)
    slug = models.SlugField()
    color = models.CharField(
        pgettext_lazy('Attribute choice value field', 'color'),
        max_length=7,
        validators=[RegexValidator('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')],
        blank=True)
    attribute = models.ForeignKey(
        ProductAttribute, related_name='values', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'attribute')

    def __str__(self):
        return self.name


class ImageManager(models.Manager):
    def first(self):
        try:
            return self.get_queryset()[0]
        except IndexError:
            pass


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name='images',
        verbose_name=pgettext_lazy('Product image field', 'product'),
        on_delete=models.CASCADE)
    image = VersatileImageField(
        upload_to='products', ppoi_field='ppoi', blank=False,
        verbose_name=pgettext_lazy('Product image field', 'image'))
    ppoi = PPOIField(verbose_name=pgettext_lazy('Product image field', 'ppoi'))
    alt = models.CharField(
        pgettext_lazy('Product image field', 'short description'),
        max_length=128, blank=True)
    order = models.PositiveIntegerField(
        pgettext_lazy('Product image field', 'order'), editable=False)

    objects = ImageManager()

    class Meta:
        ordering = ('order', )
        app_label = 'product'

    def get_ordering_queryset(self):
        return self.product.images.all()

    def save(self, *args, **kwargs):
        if self.order is None:
            qs = self.get_ordering_queryset()
            existing_max = qs.aggregate(Max('order'))
            existing_max = existing_max.get('order__max')
            self.order = 0 if existing_max is None else existing_max + 1
        super(ProductImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        qs = self.get_ordering_queryset()
        qs.filter(order__gt=self.order).update(order=F('order') - 1)
        super(ProductImage, self).delete(*args, **kwargs)


class VariantImage(models.Model):
    variant = models.ForeignKey(
        'ProductVariant', related_name='variant_images',
        verbose_name=pgettext_lazy('Variant image field', 'variant'),
        on_delete=models.CASCADE)
    image = models.ForeignKey(
        ProductImage, related_name='variant_images',
        verbose_name=pgettext_lazy('Variant image field', 'image'),
        on_delete=models.CASCADE)
