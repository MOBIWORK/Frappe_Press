<template>
	<div class="space-y-4">
		<div>
			<FormControl
				variant="outline"
				:size="size"
				:class="this.size ? 'custom-form-btn' : ''"
				:label="$t('object')"
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
				:message="`${$t('object')} ${$t('is_required')}`"
			/>
		</div>
		<div>
			<FormControl
				variant="outline"
				:size="size"
				:label="
					modelValue['enterprise'] == 'Công ty'
						? $t('company_name')
						: $t('full_name')
				"
				type="text"
				name="billing_name"
				:modelValue="modelValue['billing_name']"
				required="true"
				:onUpdate:modelValue="value => onChangeIn(value, 'billing_name')"
				:onblur="e => checkRequiredIn('billing_name', e)"
			/>
			<ErrorMessage
				class="mt-1"
				v-if="requiredFieldNotSet.includes('billing_name')"
				:message="
					modelValue['enterprise'] == 'Công ty'
						? $t('company_name')
						: $t('full_name') + ` ${$t('is_required')}`
				"
			/>
		</div>
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
				:message="field.label + ` ${$t('is_required')}`"
			/>
		</div>
		<div>
			<FormControl
				variant="outline"
				v-if="modelValue['enterprise'] == 'Công ty'"
				:size="size"
				:label="$t('tax_code')"
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
				:message="`${$t('tax_code')} ${$t('is_required')}`"
			/>
		</div>
		<div>
			<FormControl
				variant="outline"
				:size="size"
				:label="$t('address')"
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
				:message="`${$t('address')} ${$t('is_required')}`"
			/>
		</div>
		<div>
			<FormControl
				variant="outline"
				:size="size"
				:class="this.size ? 'custom-form-btn' : ''"
				:label="$t('province')"
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
				:message="`${$t('province')} ${$t('is_required')}`"
			/>
		</div>
		<div>
			<FormControl
				variant="outline"
				:size="size"
				:class="this.size ? 'custom-form-btn' : ''"
				:label="$t('county')"
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
				:message="`${$t('county')} ${$t('is_required')}`"
			/>
		</div>
	</div>
</template>

<script>
import { vietnamStates, vietnamCounty } from '@/utils/billing';
export default {
	name: 'FormCustom',
	props: ['fields', 'modelValue', 'fieldNotSet', 'size'],
	emits: ['update:modelValue'],
	data() {
		return {
			optionsEnterprise: [
				{
					label: this.$t('Company'),
					value: 'Công ty'
				},
				{
					label: this.$t('Individual'),
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
			try {
				let countys = [];
				let states = [];
				vietnamStates.forEach(el => {
					states.push({
						label: el.name,
						value: el.name
					});
				});
				vietnamCounty.forEach(el => {
					countys.push({
						value: el.name,
						parent: el.parent
					});
				});
				this.optionsState = states;
				this.optionsCountyAll = countys;
				let ops = countys.filter(d => d.parent == this.modelValue?.state);
				this.optionsCounty = ops.map(d => ({
					label: d.value,
					value: d.value
				}));
			} catch {}
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
