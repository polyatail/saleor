import React from 'react';
import ReactDOM from 'react-dom';

import VariantPicker from './variantPicker/VariantPicker';
import variantPickerStore from '../stores/variantPicker';

import {onAddToCartSuccess, onAddToCartError} from './cart';

export default $(document).ready((e) => {
  const variantPickerContainer = document.getElementById('variant-picker');

  if (variantPickerContainer) {
    const variantPickerData = JSON.parse(variantPickerContainer.dataset.variantPickerData);
    ReactDOM.render(
      <VariantPicker
        onAddToCartError={onAddToCartError}
        onAddToCartSuccess={onAddToCartSuccess}
        store={variantPickerStore}
        url={variantPickerContainer.dataset.action}
        variantAttributes={variantPickerData.variantAttributes}
        variants={variantPickerData.variants}
      />,
      variantPickerContainer
    );

  }
});
