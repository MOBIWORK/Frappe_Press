<template>
	<div>
		<FormCustom
			:size="size"
			class="mt-4"
			:fields="fields"
			:modelValue="address"
			@update:modelValue="$emit('update:address', $event)"
			:fieldNotSet="fieldNotSet"
		/>
		<!-- <div class="mt-4" v-show="address.country == 'India'">
			<FormControl
				label="GSTIN"
				v-if="gstApplicable"
				type="text"
				v-model="address.gstin"
				:disabled="!gstApplicable"
			/>
			<Button
				v-if="gstApplicable"
				class="mt-2"
				@click="
					update('gstin', 'Not Applicable');
					gstApplicable = false;
				"
			>
				I don't have a GSTIN
			</Button>
			<Button
				v-else
				class="mt-2"
				@click="
					update('gstin', '');
					gstApplicable = true;
				"
			>
				Add a GSTIN
			</Button>
		</div> -->
	</div>
</template>

<script>
import FormCustom from '@/components/FormCustom.vue';
// import { vietnamStates, vietnamCity } from '@/utils/billing';

export default {
	name: 'AddressForm',
	props: ['address', 'size'],
	emits: ['update:address'],
	components: {
		FormCustom
	},
	data() {
		return {
			fieldNotSet: [],
			gstApplicable: true
		};
	},
	watch: {
		'address.gstin'(gstin) {
			this.update('gstin', gstin);
		}
	},
	resources: {
		countryList: {
			url: 'press.api.account.country_list',
			auto: true,
			onSuccess() {
				// let country = this.countryList.find(
				// 	d => d.label === this.$account.team.country
				// );
				// if (country) {
				// 	this.update('country', country.value);
				// }
				this.update('country', 'Vietnam');
			}
		}
	},
	methods: {
		update(key, value) {
			this.$emit('update:address', {
				...this.address,
				[key]: value
			});
		},
		async validateValues() {
			let valueExists = this.fields.flat().filter(df => df.required == 1);
			let values = valueExists.map(df => this.address[df.fieldname]);
			let fieldNotSetNew = valueExists
				.filter(
					df =>
						this.address[df.fieldname] == undefined ||
						this.address[df.fieldname] == null ||
						this.address[df.fieldname] == ''
				)
				.map(df => df.fieldname);

			let fieldEx = [
				// 'state',
				// 'county',
				// 'enterprise',
				// 'billing_name',
				// 'address'
			];
			if (this.address['enterprise'] == 'Công ty') {
				fieldEx.push('tax_code');
			}
			fieldEx.forEach(el => {
				if (
					this.address[el] == undefined ||
					this.address[el] == null ||
					this.address[el] == ''
				) {
					values.push(this.address[el]);
					fieldNotSetNew.push(el);
				}
				if (el == 'phone') {
					// phone
					let rs = this.$validdateInput(this.address[el], 'phone', 0);
					if (rs[0]) {
						values.push(null);
						fieldNotSetNew.push(el);
					}
				}
			});
			this.fieldNotSet = fieldNotSetNew;

			if (!values.every(Boolean)) {
				return this.$t('please_fill_required_values');
			}

			try {
				await this.$call('press.api.billing.validate_gst', {
					address: this.address
				});
			} catch (error) {
				return error.messages.join('\n');
			}
		}
	},
	computed: {
		countryList() {
			return (this.$resources.countryList.data || []).map(d => ({
				label: d.name,
				value: d.name
			}));
		},
		fields() {
			return [
				// {
				// 	fieldtype: 'Autocomplete',
				// 	label: 'Quốc gia',
				// 	fieldname: 'country',
				// 	options: this.countryList,
				// 	required: 1
				// },
				// {
				// 	fieldtype: 'Data',
				// 	label: 'Tên công ty',
				// 	fieldname: 'billing_name',
				// 	required: 1,
				// 	size: this.size
				// },
				{
					fieldtype: 'Company name',
					label: this.$t('Company_name'),
					fieldname: 'company_name',
					required: 0,
					size: this.size
				},
				{
					fieldtype: 'Email',
					label: this.$t('Invoice_email'),
					fieldname: 'email_id',
					required: 0,
					size: this.size
				},
				{
					fieldtype: 'Data',
					label: this.$t('phone'),
					fieldname: 'phone',
					required: 0,
					size: this.size
				}
				// {
				// 	fieldtype: 'Data',
				// 	label: 'Mã số thuế',
				// 	fieldname: 'tax_code',
				// 	required: 1,
				// 	size: this.size
				// }
				// {
				// 	fieldtype: 'Data',
				// 	label: 'Địa chỉ kinh doanh',
				// 	fieldname: 'address',
				// 	required: 1,
				// 	size: this.size
				// },
				// {
				// 	fieldtype:
				// 		this.address.country === 'Vietnam' ? 'Autocomplete' : 'Data',
				// 	label: 'Tỉnh thành',
				// 	fieldname: 'state',
				// 	required: 1,
				// 	options:
				// 		this.address.country === 'Vietnam' ? this.optionsState : null,
				// 	class: this.size ? 'custom-form-btn' : ''
				// }
				// {
				// 	fieldtype:
				// 		this.address.country === 'Vietnam' ? 'Autocomplete' : 'Data',
				// 	label: 'Thành phố',
				// 	fieldname: 'county',
				// 	required: 1,
				// 	options: this.address.country === 'Vietnam' ? this.vietnamCity : null
				// }

				// {
				// 	fieldtype: 'Data',
				// 	label: 'Mã bưu điện',
				// 	fieldname: 'postal_code',
				// 	required: 1
				// }
			];
		}
	}
};
</script>
