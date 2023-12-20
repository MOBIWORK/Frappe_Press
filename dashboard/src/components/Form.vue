<template>
	<div class="space-y-4">
		<div
			v-for="field in fields"
			:key="field.fieldname"
			v-show="field.condition ? field.condition() : true"
		>
			<div class="flex space-x-4" v-if="Array.isArray(field)">
				<FormControl
					v-bind="getBindProps(subfield)"
					:key="subfield.fieldname"
					class="w-full"
					v-for="subfield in field"
				/>
			</div>
			<FormControl v-else v-bind="getBindProps(field)" />
			<ErrorMessage
				class="mt-1"
				v-if="requiredFieldNotSet.includes(field.fieldname)"
				:message="field.label + ' không được để trống'"
			/>
		</div>
		<div>
			<FormControl
				label="Quận huyện"
				:type="modelValue['country'] == 'Vietnam' ? 'autocomplete' : 'text'"
				:options="optionsCounty"
				name="county"
				:modelValue="modelValue['county']"
				required="true"
				placeholder=""
				:onUpdate:modelValue="value => onChangeIn(value, 'county')"
				:onblur="e => checkRequiredIn('county', e)"
			/>
			<ErrorMessage
				class="mt-1"
				v-if="requiredFieldNotSet.includes('county')"
				message="Quận huyện không được để trống"
			/>
		</div>
	</div>
</template>

<script>
export default {
	name: 'Form',
	props: ['fields', 'modelValue', 'fieldNotSet'],
	emits: ['update:modelValue'],
	data() {
		return {
			optionsCounty: [],
			optionsCountyAll: [],
			requiredFieldNotSet: []
		};
	},
	watch: {
		fieldNotSet(newFieldNotSet) {
			this.requiredFieldNotSet = newFieldNotSet;
		}
	},
	resources: {
		async stateList() {
			const response = await fetch(
				'https://provinces.open-api.vn/api/?depth=2'
			);
			const data = await response.json();
			let countys = [];
			data.forEach(el => {
				el.districts.forEach(ct => {
					countys.push({
						value: ct.name,
						parent: el.name
					});
				});
			});
			this.optionsCountyAll = countys;
			this.optionsCounty = this.vietnamCounty(this.modelValue?.state);
		}
	},
	methods: {
		vietnamCounty(parent) {
			let ops = this.optionsCountyAll.filter(d => d.parent == parent);
			return ops.map(d => ({
				label: d.value,
				value: d.value
			}));
		},
		onChange(value, field) {
			this.checkRequired(field, value);
			this.updateValue(field.fieldname, value);
		},
		onChangeIn(value, field) {
			this.checkRequiredIn(field, value);
			this.updateValue(field, value);
		},
		updateValue(fieldname, value) {
			let values = Object.assign({}, this.modelValue, {
				[fieldname]: value
			});
			if (fieldname == 'state') {
				this.optionsCounty = this.vietnamCounty(value?.value);
				if ('county' in values) {
					values['county'] = '';
				}
			}
			this.$emit('update:modelValue', values);
		},
		checkRequiredIn(field, value) {
			if (this.modelValue.country == 'Vietnam') {
				value = value?.value;
			}

			if (!value) {
				this.requiredFieldNotSet.push(field);
				return false;
			} else {
				this.requiredFieldNotSet = this.requiredFieldNotSet.filter(
					f => f !== field
				);
			}
			return true;
		},
		checkRequired(field, value) {
			if (value?.type == 'blur') value = value.target.value;
			if (field.required) {
				if (!value) {
					this.requiredFieldNotSet.push(field.fieldname);
					return false;
				} else {
					this.requiredFieldNotSet = this.requiredFieldNotSet.filter(
						f => f !== field.fieldname
					);
				}
			}
			return true;
		},
		getBindProps(field) {
			var propsFiled = {
				label: field.label || field.fieldname,
				type: this.getInputType(field),
				options: field.options,
				name: field.fieldname,
				modelValue: this.modelValue[field.fieldname],
				disabled: field.disabled,
				required: field.required || false,
				rows: field.rows,
				placeholder: field.placeholder,
				'onUpdate:modelValue': value => this.onChange(value, field),
				onblur: e => this.checkRequired(field, e)
			};

			return propsFiled;
		},
		getInputType(field) {
			return {
				Data: 'text',
				Int: 'number',
				Select: 'select',
				Check: 'checkbox',
				Password: 'password',
				Text: 'textarea',
				Autocomplete: 'autocomplete',
				Email: 'email'
			}[field.fieldtype || 'Data'];
		}
	}
};
</script>
