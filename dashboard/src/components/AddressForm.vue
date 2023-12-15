<template>
	<div>
		<Form
			class="mt-4"
			:fields="fields"
			:modelValue="address"
			@update:modelValue="$emit('update:address', $event)"
			:fieldNotSet="fieldNotSet"
		/>
		<div class="mt-4" v-show="address.country == 'India'">
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
		</div>
	</div>
</template>

<script>
import Form from '@/components/Form.vue';
import { vietnamStates, vietnamCity } from '@/utils/billing';

export default {
	name: 'AddressForm',
	props: ['address'],
	emits: ['update:address'],
	components: {
		Form
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
		getVietnamCity(parent = '') {
			return vietnamCity.map(d => ({
				label: d.value,
				value: d.value
			}));
		},

		update(key, value) {
			this.$emit('update:address', {
				...this.address,
				[key]: value
			});
		},
		async validateValues() {
			let { country } = this.address;
			let is_india = country == 'India';
			let valueExists = this.fields
				.flat()
				.filter(df => df.fieldname != 'gstin' || is_india);
			let values = valueExists.map(df => this.address[df.fieldname]);

			let fieldNotSetNew = valueExists
				.filter(df => !this.address[df.fieldname])
				.map(df => df.fieldname);

			if (!this.address['city']) {
				fieldNotSetNew.push('city');
				values.push(this.address['city']);
			}
			this.fieldNotSet = fieldNotSetNew;

			if (!values.every(Boolean)) {
				return 'Vui lòng điền đầy đủ thông tin';
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
		vietnamCity() {
			return vietnamCity.map(d => ({
				label: d.value,
				value: d.value
			}));
		},
		vietnamStates() {
			return vietnamStates.map(d => ({
				label: d.value,
				value: d.value
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
				{
					fieldtype: 'Email',
					label: 'Email',
					fieldname: 'email_id',
					required: 1
				},
				{
					fieldtype: 'Data',
					label: 'Số điện thoại',
					fieldname: 'phone',
					required: 1
				},
				{
					fieldtype: 'Data',
					label: 'Mã số thuế',
					fieldname: 'tax_code',
					required: 1
				},
				{
					fieldtype: 'Data',
					label: 'Địa chỉ kinh doanh',
					fieldname: 'address',
					required: 1
				},
				{
					fieldtype:
						this.address.country === 'Vietnam' ? 'Autocomplete' : 'Data',
					label: 'Tỉnh thành',
					fieldname: 'state',
					required: 1,
					options:
						this.address.country === 'Vietnam' ? this.vietnamStates : null
				}
				// {
				// 	fieldtype:
				// 		this.address.country === 'Vietnam' ? 'Autocomplete' : 'Data',
				// 	label: 'Thành phố',
				// 	fieldname: 'city',
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
