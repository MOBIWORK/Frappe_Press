<template>
	<Card :title="$t('email_notifications')">
		<template #actions>
			<Button icon-left="edit" @click="showEmailsEditDialog = true">
				{{ $t('edit') }}
			</Button>
		</template>
		<ListItem
			v-if="emailData"
			v-for="email in emailData"
			:title="fieldLabelMap[email.type] || email.type"
			:description="email.value"
			:key="email.type"
		>
		</ListItem>
		<Dialog
			:options="{
				title: $t('edit_emails'),
				actions: [
					{
						label: $t('save_changes'),
						variant: 'solid',
						onClick: () => $resources.changeEmail.submit()
					}
				]
			}"
			v-model="showEmailsEditDialog"
		>
			<template v-slot:body-content>
				<div class="mt-3" v-for="email in emailData" :key="email.type">
					<FormControl
						:label="fieldLabelMap[email.type] || email.type"
						v-model="email.value"
					/>
				</div>
				<ErrorMessage class="mt-2" :message="$resources.changeEmail.error" />
			</template>
		</Dialog>
	</Card>
</template>
<script>
export default {
	name: 'AccountEmails',
	resources: {
		getEmails() {
			return {
				url: 'press.api.account.get_emails',
				auto: true,
				onSuccess(res) {
					const noti = res.filter(r => r.type != 'marketplace_notifications');
					this.emailData = noti;
				}
			};
		},
		changeEmail() {
			return {
				url: 'press.api.account.update_emails',
				params: {
					data: JSON.stringify(this.emailData)
				},
				onSuccess(res) {
					this.showEmailsEditDialog = false;
				}
			};
		}
	},
	data() {
		return {
			showEmailsEditDialog: false,
			emailData: []
		};
	},
	computed: {
		fieldLabelMap() {
			return {
				invoices: this.$t('accountemails_content_1'),
				marketplace_notifications: this.$t('accountemails_content_2')
			};
		}
	}
};
</script>
