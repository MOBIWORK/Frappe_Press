<template>
	<Alert
		title="Kích hoạt trang web"
		v-if="site.status == 'Active' && !site.setup_wizard_complete"
	>
		<span>
			Vui lòng đăng nhập và hoàn thành hướng dẫn thiết lập trên trang web của
			bạn. Dữ liệu phân tích sẽ chỉ được thu thập sau khi quá trình thiết lập
			hoàn tất.
		</span>
		<template #actions>
			<Button
				variant="solid"
				@click="$resources.loginAsAdmin.submit()"
				:loading="$resources.loginAsAdmin.loading"
			>
				Đăng nhập
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
