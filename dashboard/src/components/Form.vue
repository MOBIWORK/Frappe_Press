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
				variant="outline"
				:size="size"
				:class="this.size ? 'custom-form-btn' : ''"
				label="Loại doanh nghiệp"
				type="select"
				:options="optionsEnterprise"
				name="enterprise"
				:modelValue="modelValue['enterprise']"
				required="true"
				:onUpdate:modelValue="value => onChangeIn(value, 'enterprise')"
				:onblur="e => checkRequiredIn('enterprise', e)"
			/>
			<ErrorMessage
				class="mt-1"
				v-if="requiredFieldNotSet.includes('enterprise')"
				message="Loại doanh nghiệp không được để trống"
			/>
		</div>
		<div>
			<FormControl
				variant="outline"
				v-if="modelValue['enterprise'] == 'Công ty'"
				:size="size"
				label="Mã số thuế"
				type="text"
				name="tax_code"
				:modelValue="modelValue['tax_code']"
				required="true"
				:onUpdate:modelValue="value => onChangeIn(value, 'tax_code')"
				:onblur="e => checkRequiredIn('tax_code', e)"
			/>
			<ErrorMessage
				class="mt-1"
				v-if="requiredFieldNotSet.includes('tax_code')"
				message="Mã số thuế không được để trống"
			/>
		</div>
		<div>
			<FormControl
				variant="outline"
				:size="size"
				label="Địa chỉ kinh doanh"
				type="text"
				name="address"
				:modelValue="modelValue['address']"
				required="true"
				:onUpdate:modelValue="value => onChangeIn(value, 'address')"
				:onblur="e => checkRequiredIn('address', e)"
			/>
			<ErrorMessage
				class="mt-1"
				v-if="requiredFieldNotSet.includes('address')"
				message="Địa chỉ kinh doanh không được để trống"
			/>
		</div>
		<div>
			<FormControl
				variant="outline"
				:size="size"
				:class="this.size ? 'custom-form-btn' : ''"
				label="Tỉnh thành"
				:type="modelValue['country'] == 'Vietnam' ? 'autocomplete' : 'text'"
				:options="optionsState"
				name="state"
				:modelValue="modelValue['state']"
				required="true"
				:onUpdate:modelValue="value => onChangeIn(value, 'state')"
				:onblur="e => checkRequiredIn('state', e)"
			/>
			<ErrorMessage
				class="mt-1"
				v-if="requiredFieldNotSet.includes('state')"
				message="Tỉnh thành không được để trống"
			/>
		</div>
		<div>
			<FormControl
				variant="outline"
				:size="size"
				:class="this.size ? 'custom-form-btn' : ''"
				label="Quận huyện"
				:type="modelValue['country'] == 'Vietnam' ? 'autocomplete' : 'text'"
				:options="optionsCounty"
				name="county"
				:modelValue="modelValue['county']"
				required="true"
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
	props: ['fields', 'modelValue', 'fieldNotSet', 'size'],
	emits: ['update:modelValue'],
	data() {
		return {
			optionsEnterprise: [
				{
					label: 'Công ty',
					value: 'Công ty'
				},
				{
					label: 'Cá nhân',
					value: 'Cá nhân'
				}
			],
			optionsCounty: [],
			optionsState: [],
			optionsCountyAll: [],
			requiredFieldNotSet: []
		};
	},
	watch: {
		modelValue(values) {
			if (this.optionsState.length == 0) {
				this.stateList();
			}
		},
		fieldNotSet(newFieldNotSet) {
			this.requiredFieldNotSet = newFieldNotSet;
		}
	},
	methods: {
		async stateList() {
			const response = await fetch(
				'https://provinces.open-api.vn/api/?depth=2'
			);
			const data = await response.json();
			let countys = [];
			let states = [];
			data.forEach(el => {
				states.push({
					label: el.name,
					value: el.name
				});
				el.districts.forEach(ct => {
					countys.push({
						value: ct.name,
						parent: el.name
					});
				});
			});
			this.optionsState = states;
			this.optionsCountyAll = countys;
			let ops = countys.filter(d => d.parent == this.modelValue?.state);
			this.optionsCounty = ops.map(d => ({
				label: d.value,
				value: d.value
			}));
		},
		vietnamCounty(parent) {
			let ops = this.optionsCountyAll.filter(d => d.parent == parent);
			return ops.map(d => ({
				label: d.value,
				value: d.value
			}));
		},
		onChange(value, field) {
			if (field.fieldname == 'phone') {
				value = value.replace(/[^0-9]/gm, '');
			}
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
			if (value?.type == 'blur') value = value.target.value;
			if (this.modelValue.country == 'Vietnam') {
				if (['county', 'state'].includes(field)) {
					value = value?.value;
				}
			}

			if (value == undefined || value == null || value == '') {
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
				if (value == undefined || value == null || value == '') {
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
				size: field.size,
				class: field.class,
				variant: 'outline',
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
