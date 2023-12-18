<template>
	<Dialog
		:options="{
			title: 'Di chuyển trang web sang bench khác',
			actions: [
				{
					label: 'Xác nhận',
					loading: this.$resources.changeGroup.loading,
					disabled: !$resources.changeGroupOptions?.data?.length,
					variant: 'solid',
					onClick: () =>
						$resources.changeGroup.submit({
							group: targetGroup,
							name: site?.name
						})
				}
			]
		}"
		v-model="show"
	>
		<template #body-content>
			<LoadingIndicator
				class="mx-auto h-4 w-4"
				v-if="$resources.changeGroupOptions.loading"
			/>
			<FormControl
				v-else-if="$resources.changeGroupOptions.data.length > 0"
				label="Chọn Bench"
				type="select"
				:options="
					$resources.changeGroupOptions.data.map(group => ({
						label: group.title,
						value: group.name
					}))
				"
				v-model="targetGroup"
			/>
			<p v-else class="text-md text-base text-gray-800">
				Không có bench khác mà bạn sở hữu cho trang web này để di chuyển đến.
			</p>
			<ErrorMessage class="mt-3" :message="$resources.changeGroup.error" />
		</template>
	</Dialog>
</template>

<script>
import { notify } from '@/utils/toast';

export default {
	name: 'SiteChangeGroupDialog',
	props: ['site', 'modelValue'],
	emits: ['update:modelValue'],
	data() {
		return {
			targetGroup: null
		};
	},
	watch: {
		show(value) {
			if (value) this.$resources.changeGroupOptions.fetch();
		}
	},
	computed: {
		show: {
			get() {
				return this.modelValue;
			},
			set(value) {
				this.$emit('update:modelValue', value);
			}
		}
	},
	resources: {
		changeGroup() {
			return {
				url: 'press.api.site.change_group',
				params: {
					name: this.site?.name
				},
				onSuccess() {
					const destinationGroupTitle =
						this.$resources.changeGroupOptions.data.find(
							group => group.name === this.targetGroup
						).title;

					notify({
						title: 'Thay bench đã Được lên lịch',
						message: `Trang web đã được lên lịch để được di chuyển đến <b>${destinationGroupTitle}</b>`,
						color: 'green',
						icon: 'check'
					});
					this.targetGroup = null;
					this.$emit('update:modelValue', false);
				}
			};
		},
		changeGroupOptions() {
			return {
				url: 'press.api.site.change_group_options',
				params: {
					name: this.site?.name
				},
				onSuccess(data) {
					if (data.length > 0) this.targetGroup = data[0].name;
				}
			};
		}
	}
};
</script>
