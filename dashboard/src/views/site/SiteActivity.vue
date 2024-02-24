<template>
	<Card
		class="h-full max-h-96 min-h-full"
		:title="$t('Site_Activity')"
		:subtitle="$t('Log_of_activities_performed_on_your_site')"
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
				{{ $t('load_more') }}
			</Button>
		</div>

		<template v-slot:actions>
			<Button @click="showChangeNotifyEmailDialog = true">
				{{ $t('Change_Notify_Email') }}
			</Button>
		</template>
		<Dialog
			:options="{
				title: $t('Change_Notify_Email'),
				actions: [
					{
						label: $t('save_changes'),
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
						title: $t('Notify_Email_Changed'),
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
				description += `${this.$t('Reason')}: ${activity.reason}\n`;
			}
			description += this.$formatDateDetail(activity.creation);
			return description;
		}
	}
};
</script>
