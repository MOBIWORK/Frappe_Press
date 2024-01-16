<template>
	<LoginBox>
		<div>
			<div>
				<div class="mb-4 w-36">
					<FormControl
						type="select"
						:options="[
							{
								label: 'Tiếng Việt',
								value: 'vi'
							}
						]"
						size="md"
						variant="outline"
						placeholder="Placeholder"
						:disabled="false"
						label=""
						modelValue="vi"
					>
						<template #prefix>
							<img src="../../assets/icon_flag_vi.svg" alt="Flag Icon" />
						</template>
					</FormControl>
				</div>
				<div class="mb-4 text-3xl font-[500] text-gray-900">
					<div>Khảo sát sơ bộ</div>
				</div>
				<div ref="address-form">
					<p class="text-base" v-if="message">
						{{ message }}
					</p>
					<div class="mt-3">
						<div class="mb-1">
							<label class="typo__label text-lg text-gray-600"
								>Lĩnh vực kinh doanh</label
							>
						</div>
						<multiselect
							v-model="valueAreasOfConcern"
							placeholder="Tìm kiếm lĩnh vực"
							label="name"
							track-by="name"
							:options="optionsAreasOfConcern"
							:multiple="true"
							:show-labels="false"
							@select="
								value => onChangeAreasOfConcern(value, 'areas_of_concern')
							"
							@remove="
								value => onChangeAreasOfConcern(value, 'areas_of_concern')
							"
							:taggable="true"
							@tag="addTag"
						>
							<template v-slot:noResult>
								<span>Không tìm thấy lĩnh vực nào.</span>
							</template>
							<template v-slot:noOptions>
								<span>Không có lĩnh vực nào.</span>
							</template>
						</multiselect>
					</div>
					<div class="mt-3">
						<FormControl
							size="lg"
							label="Quy mô nhân sự"
							type="text"
							variant="outline"
							name="number_of_employees"
							:modelValue="billingInformation['number_of_employees']"
							required="true"
							:onUpdate:modelValue="
								value => onChangeIn(value, 'number_of_employees')
							"
							:onblur="e => checkRequiredIn('number_of_employees', e)"
						/>
						<ErrorMessage
							class="mt-1"
							v-if="requiredFieldNotSet.includes('number_of_employees')"
							message="Quy mô nhân sự không được để trống"
						/>
					</div>
					<div class="mt-3">
						<div class="mb-1">
							<label class="typo__label text-lg text-gray-600"
								>Tính năng quan tâm</label
							>
						</div>
						<multiselect
							v-model="valueConcernsFeature"
							placeholder="Tìm kiếm tính năng"
							label="name"
							track-by="name"
							:options="optionsConcernsFeature"
							:multiple="true"
							:show-labels="false"
							@select="
								value => onChangeAreasOfConcern(value, 'concerns_feature')
							"
							@remove="
								value => onChangeAreasOfConcern(value, 'concerns_feature')
							"
						>
							<template v-slot:noResult>
								<span>Không tìm thấy tính năng nào.</span>
							</template>
							<template v-slot:noOptions>
								<span>Không có tính năng nào.</span>
							</template>
						</multiselect>
					</div>
					<ErrorMessage
						class="mt-2"
						:message="$resources.updateBillingInformation.error"
					/>
				</div>
				<div class="text-center">
					<Button
						class="my-6 h-9 bg-red-600 px-8 text-base font-[700] text-white hover:bg-red-700"
						variant="solid"
						:loading="$resources.updateBillingInformation.loading"
						:onClick="() => $resources.updateBillingInformation.submit()"
					>
						Gửi thông tin
					</Button>
				</div>
			</div>
		</div>
	</LoginBox>
</template>

<script>
import LoginBox from '@/views/partials/LoginBox.vue';
import { notify } from '@/utils/toast';
import Multiselect from 'vue-multiselect';

export default {
	name: 'SetupAccountPreliminarySurvey',
	props: ['message'],
	components: {
		Multiselect,
		LoginBox
	},
	data() {
		return {
			requiredFieldNotSet: [],
			billingInformation: {
				number_of_employees: '',
				concerns_feature: '',
				areas_of_concern: ''
			},
			valueAreasOfConcern: null,
			optionsAreasOfConcern: [
				{
					name: 'Bất động sản',
					value: 'Bất động sản'
				},
				{
					name: 'Giáo dục',
					value: 'Giáo dục'
				},
				{
					name: 'Bia - Rượu - Nước giải khát',
					value: 'Bia - Rượu - Nước giải khát'
				},
				{
					name: 'Dược phẩm - Y tế',
					value: 'Dược phẩm - Y tế'
				},
				{
					name: 'Thiết bị vệ sinh',
					value: 'Thiết bị vệ sinh'
				},
				{
					name: 'Vật liệu xây dựng',
					value: 'Vật liệu xây dựng'
				},
				{
					name: 'Hóa mỹ phẩm',
					value: 'Hóa mỹ phẩm'
				},
				{
					name: 'Vật tư Nông nghiệp - Nông Dược',
					value: 'Vật tư Nông nghiệp - Nông Dược'
				},
				{
					name: 'Hàng tiêu dùng',
					value: 'Hàng tiêu dùng'
				},
				{
					name: 'Thiết bị điện - Điện tử - Điện lạnh',
					value: 'Thiết bị điện - Điện tử - Điện lạnh'
				},
				{
					name: 'Thực phẩm',
					value: 'Thực phẩm'
				},
				{
					name: 'Xây dựng',
					value: 'Xây dựng'
				}
			],
			valueConcernsFeature: null,
			optionsConcernsFeature: []
		};
	},
	resources: {
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
						title: 'Gửi thông tin thành công!'
					});
					// this.$router.push('/sites/new');
					window.location.href = '/sites/new';
				},
				validate() {
					return this.validateValues();
				}
			};
		}
	},
	methods: {
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
			let fieldEx = ['number_of_employees'];

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
				return 'Vui lòng điền đầy đủ thông tin';
			}
		},
		validPhone(e) {
			let value = e.target.value.replace(/[^0-9]/gm, '');
			this.phone = value;
		},
		onChangeIn(value, field) {
			this.checkRequiredIn(field, value);
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
