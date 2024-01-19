<template>
	<Card
		class="h-full max-h-96 min-h-full"
		title="Hoạt động tổ chức"
		subtitle="Các hoạt động được thực hiện trên tổ chức của bạn"
	>
		<div class="divide-y">
			<ListItem
				v-for="a in activities.data"
				:key="a.creation"
				:title="`${a.action} by ${a.owner}`"
				:description="getDescription(a)"
			/>
		</div>
		<div class="my-2" v-if="$resources.activities.hasNextPage">
			<Button
				:loading="$resources.activities.list.loading"
				loadingText="Fetching..."
				@click="$resources.activities.next()"
			>
				Tải thêm
			</Button>
		</div>

		<template v-slot:actions>
			<Button @click="showChangeNotifyEmailDialog = true">
				Thay đổi email thông báo
			</Button>
		</template>
		<Dialog
			:options="{
				title: 'Thay đổi email thông báo',
				actions: [
					{
						label: 'Lưu thay đổi',
						variant: 'solid',
						loading: $resources.changeNotifyEmail.loading,
						onClick: () => $resources.changeNotifyEmail.submit()
					}
				]
			}"
			v-model="showChangeNotifyEmailDialog"
		>
			<template v-slot:body-content>
				<FormControl v-model="site.notify_email" />
			</template>
		</Dialog>
	</Card>
</template>

<script>
import { notify } from '@/utils/toast';

export default {
	name: 'SiteActivity',
	props: ['site'],
	resources: {
		activities() {
			return {
				type: 'list',
				doctype: 'Site Activity',
				url: 'press.api.site.activities',
				filters: {
					site: this.site?.name
				},
				start: 0,
				auto: true,
				pageLength: 20
			};
		},
		changeNotifyEmail() {
			return {
				url: 'press.api.site.change_notify_email',
				params: {
					name: this.site?.name,
					email: this.site?.notify_email
				},
				onSuccess() {
					this.showChangeNotifyEmailDialog = false;
					notify({
						title: 'Email thông báo đã được thay đổi!',
						icon: 'check',
						color: 'green'
					});
				}
			};
		}
	},
	computed: {
		activities() {
			return this.$resources.activities;
		}
	},
	data() {
		return {
			showChangeNotifyEmailDialog: false
		};
	},
	methods: {
		getDescription(activity) {
			let description = '';
			if (activity.reason) {
				description += `Lý do: ${activity.reason}\n`;
			}
			description += this.$formatDateDetail(activity.creation);
			return description;
		}
	}
};
</script>
