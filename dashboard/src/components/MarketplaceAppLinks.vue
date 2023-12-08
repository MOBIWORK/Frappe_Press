<template>
	<Card title="Liên kết" subtitle="Sẽ được hiển thị trên marketplace">
		<template #actions>
			<Button icon-left="edit" @click="showEditLinksDialog = true">Edit</Button>
		</template>
		<Dialog
			:options="{
				title: 'Cập nhật liên kết',
				actions: [
					{
						variant: 'solid',
						label: 'Lưu thay đổi',
						loading: $resources.updateAppLinks.loading,
						onClick: () => $resources.updateAppLinks.submit()
					}
				]
			}"
			v-model="showEditLinksDialog"
		>
			<template v-slot:body-content>
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
					<FormControl label="Trang web" v-model="app.website" />
					<FormControl label="Hỗ trợ" v-model="app.support" />
					<FormControl label="Tài liệu" v-model="app.documentation" />
					<FormControl
						label="Chính sách quyền riêng tư"
						v-model="app.privacy_policy"
					/>
					<FormControl
						label="Điều khoản dịch vụ"
						v-model="app.terms_of_service"
					/>
				</div>

				<ErrorMessage class="mt-4" :message="$resources.updateAppLinks.error" />
			</template>
		</Dialog>
		<div class="divide-y" v-if="app">
			<ListItem title="Trang web" :description="app.website || 'N/A'" />
			<ListItem title="Hỗ trợ" :description="app.support || 'N/A'" />
			<ListItem title="Tài liệu" :description="app.documentation || 'N/A'" />
			<ListItem
				title="Chính sách quyền riêng tư"
				:description="app.privacy_policy || 'N/A'"
			/>
			<ListItem
				title="Điều khoản dịch vụ"
				:description="app.terms_of_service || 'N/A'"
			/>
		</div>
	</Card>
</template>

<script>
import { notify } from '@/utils/toast';

export default {
	name: 'MarketplaceAppLinks',
	props: {
		app: Object
	},
	data() {
		return {
			showEditLinksDialog: false
		};
	},
	resources: {
		updateAppLinks() {
			return {
				url: 'press.api.marketplace.update_app_links',
				params: {
					name: this.app.name,
					links: {
						website: this.app.website,
						support: this.app.support,
						documentation: this.app.documentation,
						privacy_policy: this.app.privacy_policy,
						terms_of_service: this.app.terms_of_service
					}
				},
				onSuccess() {
					this.showEditLinksDialog = false;
					notify({
						title: 'Liên kết đã được cập nhật!',
						icon: 'check',
						color: 'green'
					});
				}
			};
		}
	}
};
</script>
