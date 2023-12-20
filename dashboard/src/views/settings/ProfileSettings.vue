<template>
	<div class="space-y-5">
		<AccountProfile />
		<AccountEmails />
		<AccountReferral
			v-if="this.$account.feature_flags.enabled_refer_earn == 1"
		/>
	</div>
</template>

<script>
import AccountProfile from './AccountProfile.vue';
import AccountReferral from './AccountReferral.vue';
import AccountEmails from './AccountEmails.vue';

export default {
	name: 'AccountSettings',
	pageMeta() {
		return {
			title: 'Settings - Profile'
		};
	},
	components: {
		AccountProfile,
		AccountReferral,
		AccountEmails
	}
};
</script>
