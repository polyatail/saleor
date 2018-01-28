import React from 'react';
import ReactDOM from 'react-dom';

import VariantPicker from './variantPicker/VariantPicker';
import variantPickerStore from '../stores/variantPicker';

import {onAddToCartSuccess, onAddToCartError} from './cart';

const variantPickerContainer = document.getElementsByClassName('variant-picker');

for (var i = 0; i < variantPickerContainer.length; i++)
{
  console.log(i);
  console.log(variantPickerContainer[i].dataset.variantPickerData);

  if (variantPickerContainer[i].dataset.variantPickerData)
  {
    var variantData = JSON.parse(variantPickerContainer[i].dataset.variantPickerData);
    var variantDataStore = new variantPickerStore();
  
    ReactDOM.render(
      <VariantPicker
        onAddToCartError={onAddToCartError}
        onAddToCartSuccess={onAddToCartSuccess}
        store={variantDataStore}
        url={variantPickerContainer[i].dataset.action}
        variantAttributes={variantData.variantAttributes}
        variants={variantData.variants}
      />,
      variantPickerContainer[i]
    );
  }
}
