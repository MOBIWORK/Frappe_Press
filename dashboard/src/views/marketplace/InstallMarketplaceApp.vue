<template>
	<div class="px-4 py-4 text-base sm:px-8">
		<Button v-if="$resources.opionsForQuickInstall" :loading="true">{{
			$t('Loading')
		}}</Button>
		<div v-else>
			<h1 class="mb-4 text-xl font-semibold">
				{{ $t('Install_App') }}: {{ options ? options.title : '' }}
			</h1>

			<ErrorMessage :message="$resources.optionsForQuickInstall.error" />

			<div v-if="options" class="mt-2 grid grid-cols-1 gap-2 md:grid-cols-2">
				<Card
					:title="$t('Sites')"
					:subtitle="
						options.sites?.length ? $t('Select_a_site_to_install') : ''
					"
				>
					<ul v-if="options.sites?.length">
						<li
							v-for="site in options.sites"
							class="flex w-full flex-row justify-between rounded-md px-1 py-2 text-left text-base hover:bg-gray-50"
						>
							<p>
								{{ site }}
							</p>
							<Button
								@click="installAppOnSite(site)"
								:loading="$resources.installAppOnSite.loading"
								>{{ $t('Install') }}</Button
							>
						</li>
					</ul>

					<div v-else>
						<p class="text-sm text-gray-700">
							{{ $t('No_site_available_for_install') }}
						</p>
					</div>

					<template v-slot:actions>
						<Button variant="solid" route="/sites/new">{{
							$t('New_Site')
						}}</Button>
					</template>
				</Card>

				<Card
					:title="$t('Private_Benches')"
					:subtitle="
						options.release_groups?.length
							? $t('Select_a_bench_to_install')
							: ''
					"
				>
					<ul v-if="options.release_groups?.length" class="space-y-3">
						<li
							v-for="bench in options.release_groups"
							class="flex w-full flex-row justify-between rounded-md px-1 py-2 text-left text-base hover:bg-gray-50"
						>
							<p>
								{{ bench.title }}
							</p>
							<Button
								@click="addAppToBench(bench)"
								:loading="$resources.addAppToBench.loading"
								>{{ $t('Add') }}</Button
							>
						</li>
					</ul>

					<div v-else>
						<p class="text-sm text-gray-700">
							{{ $t('No_benches_available_for_install') }}
						</p>
					</div>
					<!-- <template v-slot:actions>
						<Button variant="solid" route="/benches/new">{{ $t('New_Bench') }}</Button>
					</template> -->
				</Card>
			</div>
		</div>

		<Dialog
			v-model="showPlanSelectionDialog"
			:options="{
				title: $t('Select_app_plan'),
				size: 'xl'
			}"
		>
			<template v-slot:body-content>
				<ChangeAppPlanSelector
					v-if="marketplaceApp"
					:app="marketplaceApp"
					class="mb-9"
					@change="plan => (selectedPlan = plan.name)"
				/>
				<ErrorMessage :message="$resources.installAppOnSite.error" />
			</template>
			<template v-slot:actions>
				<Button
					variant="solid"
					:loading="$resources.installAppOnSite.loading"
					@click="installAppOnSite(selectedSite)"
					>{{ $t('Proceed') }}</Button
				>
			</template>
		</Dialog>
	</div>
</template>

<script>
import ChangeAppPlanSelector from '@/components/ChangeAppPlanSelector.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'InstallMarketplaceApp',
	props: ['marketplaceApp'],
	data() {
		return {
			showPlanSelectionDialog: false,
			selectedSite: null,
			selectedBench: null,
			selectedPlan: null
		};
	},
	components: {
		ChangeAppPlanSelector
	},
	resources: {
		optionsForQuickInstall() {
			return {
				url: 'press.api.marketplace.options_for_quick_install',
				params: {
					marketplace_app: this.marketplaceApp
				},
				auto: true
			};
		},
		addAppToBench() {
			return {
				url: 'press.api.bench.add_app',
				onSuccess() {
					notify({
						title: this.$t('InstallMarketplaceApp_content_1'),
						icon: 'check',
						color: 'green'
					});

					this.$router.push(`/benches/${this.selectedBench}/apps`);
				}
			};
		},
		installAppOnSite() {
			return {
				url: 'press.api.site.install_app',
				validate() {
					if (this.showPlanSelectionDialog && !this.selectedPlan) {
						return this.$t('Please_select_a_plan_to_continue');
					}
				},
				onSuccess() {
					notify({
						title: this.$t('InstallMarketplaceApp_content_2'),
						icon: 'check',
						color: 'green'
					});

					this.selectedPlan = null;
					this.selectedSite = null;
					this.showPlanSelectionDialog = false;
					this.$resources.optionsForQuickInstall.fetch();
				}
			};
		}
	},
	methods: {
		addAppToBench(group) {
			this.selectedBench = group.name;

			this.$resources.addAppToBench.submit({
				name: group.name,
				source: group.source,
				app: this.options.app_name
			});
		},

		installAppOnSite(site) {
			this.selectedSite = site;

			// If paid app, show plan selection dialog
			if (this.options.has_plans_available && !this.showPlanSelectionDialog) {
				this.showPlanSelectionDialog = true;
				return;
			}

			this.$resources.installAppOnSite.submit({
				name: site,
				app: this.options.app_name,
				plan: this.selectedPlan
			});
		}
	},
	computed: {
		options() {
			if (
				this.$resources.optionsForQuickInstall.data &&
				!this.$resources.optionsForQuickInstall.loading
			) {
				return this.$resources.optionsForQuickInstall.data;
			}

			return null;
		}
	}
};
</script>
