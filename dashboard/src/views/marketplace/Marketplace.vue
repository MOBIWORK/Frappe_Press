<template>
	<div>
		<header
			class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5"
		>
			<Breadcrumbs :items="[{ label: 'Ứng dụng', route: '/marketplace' }]">
				<template #actions>
					<Button
						variant="solid"
						icon-left="plus"
						label="Thêm mới"
						class="ml-2"
						@click="
							!$resources.appOptions.data
								? $resources.appOptions.fetch()
								: null;
							showAddAppDialog = true;
						"
					/>
				</template>
			</Breadcrumbs>
		</header>
		<SectionHeader class="mx-5 mt-6" heading="Ứng dụng" />

		<Dialog
			:options="{
				title: 'Thêm ứng dụng vào marketplace',
				size: 'xl'
			}"
			v-model="showAddAppDialog"
		>
			<template v-slot:body-content>
				<LoadingText class="py-2" v-if="$resources.appOptions.loading" />
				<AppSourceSelector
					v-else-if="
						$resources.appOptions.data && $resources.appOptions.data.length > 0
					"
					class="mt-1"
					:apps="availableApps"
					v-model="selectedApp"
					:multiple="false"
				/>
				<p v-else class="text-base">Không có nguồn ứng dụng khả dụng.</p>

				<ErrorMessage
					class="mt-2"
					:message="$resources.addMarketplaceApp.error"
				/>

				<p class="mt-4 text-base" @click="showAddAppDialog = false">
					Không tìm thấy ứng dụng của bạn ở đây?
					<Link :to="`/marketplace/apps/new`"> Thêm từ GitHub </Link>
				</p>
			</template>
			<template #actions>
				<Button
					variant="solid"
					class="ml-2 w-full"
					v-if="selectedApp"
					:loading="$resources.addMarketplaceApp.loading"
					@click="
						$resources.addMarketplaceApp.submit({
							source: selectedApp.source.name,
							app: selectedApp.app
						})
					"
				>
					Thêm {{ selectedApp.app }}
				</Button>
			</template>
		</Dialog>

		<Tabs class="mx-5 mt-3 pb-32" :tabs="tabs">
			<router-view v-if="$account.team"></router-view>
		</Tabs>
	</div>
</template>

<script>
import Tabs from '@/components/Tabs.vue';
import AppSourceSelector from '@/components/AppSourceSelector.vue';

export default {
	name: 'Marketplace',
	pageMeta() {
		return {
			title: 'Developer - MBW Cloud'
		};
	},
	components: {
		Tabs,
		AppSourceSelector
	},
	data: () => ({
		tabs: [
			{ label: 'Ứng dụng của tôi', route: '/marketplace/apps' },
			{ label: 'Hồ sơ nhà xuất bản', route: '/marketplace/publisher-profile' },
			{ label: 'Tiền chi trả', route: '/marketplace/payouts' }
		],
		showAddAppDialog: false,
		selectedApp: null
	}),
	resources: {
		appOptions() {
			return {
				url: 'press.api.marketplace.options_for_marketplace_app'
			};
		},
		addMarketplaceApp() {
			return {
				url: 'press.api.marketplace.add_app',
				onSuccess() {
					this.showAddAppDialog = false;
					window.location.reload();
				}
			};
		}
	},
	computed: {
		availableApps() {
			return this.$resources.appOptions.data;
		}
	},
	activated() {
		if (this.$route.matched.length === 1) {
			let path = this.$route.fullPath;
			this.$router.replace(`${path}/apps`);
		}
	},
	beforeRouteUpdate(to, from, next) {
		if (to.path == '/marketplace') {
			next('/marketplace/apps');
		} else {
			next();
		}
	}
};
</script>
