import React from 'react';
import ReactDOM from 'react-dom';

import ProductSchema from './variantPicker/ProductSchema';
import variantPickerStore from '../stores/variantPicker';

export default $(document).ready((e) => {
  const productSchemaContainer = document.getElementById('product-schema-component');
  const productSchemaStore = new variantPickerStore();
  if (productSchemaContainer) {
    let productSchema = JSON.parse(document.getElementById('product-schema-component').children[0].text);
    ReactDOM.render(
      <ProductSchema
        variantStore={productSchemaStore}
        productSchema={productSchema}
      />,
      productSchemaContainer
    );
  }
});
