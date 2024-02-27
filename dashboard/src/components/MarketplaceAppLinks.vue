<template>
	<Card :title="$t('Links')" :subtitle="$t('MarketplaceAppLinks_content_1')">
		<template #actions>
			<Button icon-left="edit" @click="showEditLinksDialog = true">{{
				$t('Edit')
			}}</Button>
		</template>
		<Dialog
			:options="{
				title: $t('Update_Links'),
				actions: [
					{
						variant: 'solid',
						label: $t('save_changes'),
						loading: $resources.updateAppLinks.loading,
						onClick: () => $resources.updateAppLinks.submit()
					}
				]
			}"
			v-model="showEditLinksDialog"
		>
			<template v-slot:body-content>
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
					<FormControl :label="$t('Website')" v-model="app.website" />
					<FormControl :label="$t('Support')" v-model="app.support" />
					<FormControl
						:label="$t('Documentation')"
						v-model="app.documentation"
					/>
					<FormControl
						:label="$t('Privacy_Policy')"
						v-model="app.privacy_policy"
					/>
					<FormControl
						:label="$t('Terms_of_Service')"
						v-model="app.terms_of_service"
					/>
				</div>

				<ErrorMessage class="mt-4" :message="$resources.updateAppLinks.error" />
			</template>
		</Dialog>
		<div class="divide-y" v-if="app">
			<ListItem :title="$t('Website')" :description="app.website || 'N/A'" />
			<ListItem :label="$t('Support')" :description="app.support || 'N/A'" />
			<ListItem
				:label="$t('Documentation')"
				:description="app.documentation || 'N/A'"
			/>
			<ListItem
				:label="$t('Privacy_Policy')"
				:description="app.privacy_policy || 'N/A'"
			/>
			<ListItem
				:label="$t('Terms_of_Service')"
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
						title: this.$t('MarketplaceAppLinks_content_2'),
						icon: 'check',
						color: 'green'
					});
				}
			};
		}
	}
};
</script>
