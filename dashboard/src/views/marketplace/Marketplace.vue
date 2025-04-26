<template>
	<div>
		<header
			class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5"
		>
			<Breadcrumbs :items="[{ label: $t('Apps'), route: '/marketplace' }]">
				<template #actions>
					<Button
						variant="solid"
						icon-left="plus"
						:label="$t('New')"
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
		<SectionHeader class="mx-5 mt-6" :heading="$t('Apps')" />

		<Dialog
			:options="{
				title: $t('Add_App_to_Marketplace'),
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
				<p v-else class="text-base">{{ $t('MarketplaceApp_content_1') }}</p>

				<ErrorMessage
					class="mt-2"
					:message="$resources.addMarketplaceApp.error"
				/>

				<p class="mt-4 text-base" @click="showAddAppDialog = false">
					{{ $t('MarketplaceApp_content_2') }}
					<Link :to="`/marketplace/apps/new`">
						{{ $t('Add_from_GitHub') }}
					</Link>
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
							app: selectedApp.app,
							lang: this.$i18n.locale
						})
					"
				>
					{{ $t('Add') }} {{ selectedApp.app }}
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
			title: `${this.$t('Developer')} - MBWCloud`
		};
	},
	components: {
		Tabs,
		AppSourceSelector
	},
	data() {
		return {
			tabs: this.getLangTabs(),
			showAddAppDialog: false,
			selectedApp: null
		};
	},
	watch: {
		'$i18n.locale'() {
			this.tabs = this.getLangTabs();
		}
	},
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
	methods: {
		getLangTabs() {
			return [
				{ label: this.$t('My_Apps'), route: '/marketplace/apps' },
				{
					label: this.$t('Publisher_Profile'),
					route: '/marketplace/publisher-profile'
				},
				{ label: this.$t('Payouts'), route: '/marketplace/payouts' }
			];
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
