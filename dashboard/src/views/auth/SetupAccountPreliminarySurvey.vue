<template>
	<LoginBox>
		<div>
			<div class="mb-4 w-36">
				<SelectLanguage></SelectLanguage>
			</div>
			<div class="text-center">
				<div class="mb-4 text-3xl font-[500] text-gray-900">
					<div>{{ $t('Welcome') }} {{ currenBilling.billing_name }}!</div>
				</div>
				<div class="text-sm text-gray-700">
					{{ $t('SetupAccountPreliminarySurvey_content_8') }}
					{{ $formatMoney(bonuses.free_credits_vnd, 0) }} VND
					{{ $t('SetupAccountPreliminarySurvey_content_9') }}
					{{ bonuses.number_days_promotion }}
					{{ $t('SetupAccountPreliminarySurvey_content_10') }}
				</div>
			</div>
			<div ref="address-form">
				<p class="text-base" v-if="message">
					{{ message }}
				</p>
				<div class="mt-3">
					<div class="mb-1">
						<label class="typo__label text-lg text-gray-600">{{
							$t('Operational_domain')
						}}</label>
					</div>
					<multiselect
						v-model="valueAreasOfConcern"
						:placeholder="$t('Search')"
						label="name"
						track-by="name"
						:options="optionsAreasOfConcern"
						:multiple="true"
						:show-labels="false"
						@select="value => onChangeAreasOfConcern(value, 'areas_of_concern')"
						@remove="value => onChangeAreasOfConcern(value, 'areas_of_concern')"
						:taggable="true"
						@tag="addTag"
					>
						<template v-slot:noResult>
							<span>{{ $t('SetupAccountPreliminarySurvey_content_1') }}</span>
						</template>
						<template v-slot:noOptions>
							<span>{{ $t('no_data') }}</span>
						</template>
					</multiselect>
					<ErrorMessage
						class="mt-2"
						v-if="requiredFieldNotSet.includes('areas_of_concern')"
						:message="$t('SetupAccountPreliminarySurvey_content_3')"
					/>
				</div>
				<div class="mt-3">
					<div>
						<FormControl
							name="number_of_employees"
							class="custom-form-btn"
							type="select"
							id="employee"
							size="lg"
							variant="outline"
							placeholder="---"
							:label="$t('SetupAccountPreliminarySurvey_content_2')"
							:options="opsEmployees"
							v-model="billingInformation['number_of_employees']"
							:onUpdate:modelValue="
								value => onChangeIn(value, 'number_of_employees')
							"
						/>
					</div>
					<ErrorMessage
						class="mt-1"
						v-if="requiredFieldNotSet.includes('number_of_employees')"
						:message="$t('SetupAccountPreliminarySurvey_content_3')"
					/>
				</div>
				<div class="mb-4 mt-3">
					<div class="mb-1">
						<label class="typo__label text-lg text-gray-600">{{
							$t('SetupAccountPreliminarySurvey_content_7')
						}}</label>
					</div>
					<multiselect
						v-model="valueConcernsFeature"
						:placeholder="$t('Search')"
						label="name"
						track-by="name"
						:options="optionsConcernsFeature"
						:multiple="true"
						:show-labels="false"
						@select="value => onChangeAreasOfConcern(value, 'concerns_feature')"
						@remove="value => onChangeAreasOfConcern(value, 'concerns_feature')"
					>
						<template v-slot:noResult>
							<span>{{ $t('SetupAccountPreliminarySurvey_content_5') }}</span>
						</template>
						<template v-slot:noOptions>
							<span>{{ $t('no_data') }}</span>
						</template>
					</multiselect>
					<ErrorMessage
						class="mt-2"
						v-if="requiredFieldNotSet.includes('concerns_feature')"
						:message="$t('SetupAccountPreliminarySurvey_content_3')"
					/>
				</div>
				<ErrorMessage
					class="mt-2"
					:message="this.$translateMessage(msgError)"
				/>
			</div>
			<div class="text-center">
				<Button
					class="my-6 h-9 px-8 text-base font-[700] text-white"
					variant="solid"
					:loading="$resources.updateBillingInformation.loading"
					:onClick="() => $resources.updateBillingInformation.submit()"
				>
					{{ $t('Submit_information') }}
				</Button>
			</div>
			<div class="flex justify-center">
				<router-link
					class="mb-2 text-base"
					:to="{
						name: 'Setup Account Billing'
					}"
				>
					<div class="flex justify-center">
						<img src="../../assets/icon_left.svg" />
						<span class="font-[600]"> {{ $t('Back') }}</span>
					</div>
				</router-link>
			</div>
		</div>
	</LoginBox>
</template>

<script>
import LoginBox from '@/views/partials/LoginBox.vue';
import { notify } from '@/utils/toast';
import Multiselect from 'vue-multiselect';
import SelectLanguage from '../../components/global/SelectLanguage.vue';

export default {
	name: 'SetupAccountPreliminarySurvey',
	props: ['message'],
	components: {
		Multiselect,
		LoginBox,
		SelectLanguage
	},
	data() {
		return {
			msgError: null,
			requiredFieldNotSet: [],
			billingInformation: {
				number_of_employees: '',
				concerns_feature: '',
				areas_of_concern: ''
			},
			valueAreasOfConcern: null,
			optionsAreasOfConcern: this.getOptionsAreasOfConcern(),
			valueConcernsFeature: null,
			optionsConcernsFeature: [],
			opsEmployees: this.getOpsEmployees(),
			currenBilling: {},
			bonuses: {}
		};
	},
	watch: {
		'$i18n.locale'() {
			this.optionsAreasOfConcern = this.getOptionsAreasOfConcern();
			this.opsEmployees = this.getOpsEmployees();
		}
	},
	resources: {
		currentBillingInformation: {
			url: 'press.api.account.get_billing_information',
			auto: true,
			onSuccess(data) {
				this.currenBilling = data.billing_details;
			}
		},
		bonuses: {
			url: 'press.api.account.get_information_about_registration_bonuses',
			auto: true,
			onSuccess(data) {
				this.bonuses = data;
			}
		},
		getAllCategory: {
			url: 'press.api.billing.get_all_category',
			auto: true,
			onSuccess(data) {
				this.optionsConcernsFeature = data.map(el => ({
					name: el.name,
					value: el.name
				}));
			}
		},
		updateBillingInformation() {
			return {
				url: 'press.api.account.update_information_survey',
				params: {
					billing_details: this.billingInformation
				},
				onSuccess() {
					notify({
						icon: 'check',
						color: 'green',
						title: this.$t('SetupAccountPreliminarySurvey_content_6')
					});
					// this.$router.push('/sites/new');
					window.location.href = '/dashboard/sites/new';
				},
				async validate() {
					// let a = await this.validateValues();
					// this.msgError = a;
					// if (a) {
					// 	return this.$t(a);
					// }
				}
			};
		}
	},
	methods: {
		getOpsEmployees() {
			return [
				{
					label: this.$t('SetupAccountPS_content_14'),
					value: 4
				},
				{
					label: this.$t('SetupAccountPS_content_15'),
					value: 9
				},
				{
					label: this.$t('SetupAccountPS_content_16'),
					value: 50
				},
				{
					label: this.$t('SetupAccountPS_content_17'),
					value: 200
				},
				{
					label: this.$t('SetupAccountPS_content_18'),
					value: 500
				},
				{
					label: this.$t('SetupAccountPS_content_19'),
					value: 9999
				}
			];
		},
		getOptionsAreasOfConcern() {
			return [
				{
					name: this.$t('SetupAccountPS_content_1'),
					value: 'Bất động sản'
				},
				{
					name: this.$t('SetupAccountPS_content_2'),
					value: 'Giáo dục'
				},
				{
					name: this.$t('SetupAccountPS_content_3'),
					value: 'Bia - Rượu - Nước giải khát'
				},
				{
					name: this.$t('SetupAccountPS_content_4'),
					value: 'Dược phẩm - Y tế'
				},
				{
					name: this.$t('SetupAccountPS_content_5'),
					value: 'Thiết bị vệ sinh'
				},
				{
					name: this.$t('SetupAccountPS_content_6'),
					value: 'Vật liệu xây dựng'
				},
				{
					name: this.$t('SetupAccountPS_content_7'),
					value: 'Hóa mỹ phẩm'
				},
				{
					name: this.$t('SetupAccountPS_content_8'),
					value: 'Vật tư Nông nghiệp - Nông Dược'
				},
				{
					name: this.$t('SetupAccountPS_content_9'),
					value: 'Hàng tiêu dùng'
				},
				{
					name: this.$t('SetupAccountPS_content_10'),
					value: 'Thiết bị điện - Điện tử - Điện lạnh'
				},
				{
					name: this.$t('SetupAccountPS_content_11'),
					value: 'Thực phẩm'
				},
				{
					name: this.$t('SetupAccountPS_content_12'),
					value: 'Xây dựng'
				},
				{
					name: this.$t('SetupAccountPS_content_3'),
					value: 'Khác'
				}
			];
		},
		addTag(newTag) {
			const tag = {
				name: newTag,
				code: newTag.substring(0, 2) + Math.floor(Math.random() * 10000000)
			};
			this.options.push(tag);
			this.value.push(tag);
		},
		onChangeAreasOfConcern(value, field) {
			let newValue = [];
			let data = [];
			if (field == 'areas_of_concern') {
				data = this.valueAreasOfConcern;
			} else if (field == 'concerns_feature') {
				data = this.valueConcernsFeature;
			}
			data.forEach(el => {
				newValue.push(el.value);
			});

			newValue = newValue.join(';');
			this.billingInformation[field] = newValue;
		},
		async validateValues() {
			let fieldNotSetNew = [];
			let values = [this.billingInformation.number_of_employees];
			let fieldEx = [
				'number_of_employees',
				'concerns_feature',
				'areas_of_concern'
			];

			fieldEx.forEach(el => {
				if (
					this.billingInformation[el] == undefined ||
					this.billingInformation[el] == null ||
					this.billingInformation[el] == ''
				) {
					values.push(this.billingInformation[el]);
					fieldNotSetNew.push(el);
				}
			});

			this.requiredFieldNotSet = fieldNotSetNew;

			if (!values.every(Boolean)) {
				return 'please_fill_required_values';
			}
		},
		onChangeIn(value, field) {
			if (field == 'number_of_employees') {
				value = value.replace(/[^0-9]/gm, '');
			}
			this.billingInformation[field] = value;
		},
		checkRequiredIn(field, value) {
			if (value?.type == 'blur') value = value.target.value;

			if (value == undefined || value == null || value == '') {
				this.requiredFieldNotSet.push(field);
				return false;
			} else {
				this.requiredFieldNotSet = this.requiredFieldNotSet.filter(
					f => f !== field
				);
			}
			return true;
		}
	}
};
</script>

<style src="vue-multiselect/dist/vue-multiselect.css"></style>
