<template>
	<Alert
		:title="$t('site_activation')"
		v-if="site.status == 'Active' && !site.setup_wizard_complete"
	>
		<span>
			{{ $t('AlertSiteActivation_content_1') }}
		</span>
		<template #actions>
			<Button
				variant="solid"
				@click="$resources.loginAsAdmin.submit()"
				:loading="$resources.loginAsAdmin.loading"
			>
				{{ $t('login') }}
			</Button>
		</template>
	</Alert>
</template>
<script>
import { loginAsAdmin } from '@/controllers/loginAsAdmin';
export default {
	name: 'AlertSiteActivation',
	props: ['site'],
	resources: {
		loginAsAdmin() {
			return loginAsAdmin(this.site?.name);
		}
	}
};
</script>
