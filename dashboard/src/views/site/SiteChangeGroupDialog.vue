<template>
	<Dialog
		:options="{
			title: $t('move_site_to_another_bench'),
			actions: [
				{
					label: $t('confirm'),
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
				:label="$t('select_bench')"
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
				{{ $t('SiteChangeGroupDialog_content_1') }}
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
					name: this.site?.name,
					lang: this.$i18n.locale
				},
				onSuccess() {
					const destinationGroupTitle =
						this.$resources.changeGroupOptions.data.find(
							group => group.name === this.targetGroup
						).title;

					notify({
						title: this.$t('scheduled_bench_change'),
						message: `${this.$t(
							'SiteChangeGroupDialog_content_2'
						)} <b>${destinationGroupTitle}</b>`,
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
