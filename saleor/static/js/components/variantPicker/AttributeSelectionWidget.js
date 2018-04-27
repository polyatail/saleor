import React, { Component, PropTypes } from 'react';
import classNames from 'classnames';

export default class AttributeSelectionWidget extends Component {
  static propTypes = {
    attribute: PropTypes.object.isRequired,
    handleChange: PropTypes.func.isRequired,
    selected: PropTypes.string
  };

  change = (event) => {
    this.props.selected = this.props.attribute.values[event.target.value].pk.toString();
    this.props.handleChange(this.props.attribute.pk.toString(),
                            this.props.attribute.values[event.target.value].pk.toString());
  }

  render() {
    const { attribute, selected } = this.props;
    return (
      <div className="variant-picker">
        <div className="form-group">
          <label className="control-label">{attribute.name}</label>
          <select
            className="form-control"
            onChange={this.change}>
            {attribute.values.map((value, i) => {
              const active = selected === value.pk.toString();
              return (
                <option value={i} selected={active}>
                  {value.name}
                </option>
              );
            })};
          </select>
        </div>
      </div>
    );
  }
}
