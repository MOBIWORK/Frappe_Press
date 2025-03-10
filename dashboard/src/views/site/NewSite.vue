<template>
	<div>
		<header
			class="sticky top-0 z-10 flex flex-wrap items-center justify-between border-b bg-white px-5 py-2.5"
		>
			<Breadcrumbs
				:items="[
					{ label: $t('sites'), route: { name: 'Sites' } },
					{ label: $t('New'), route: { name: 'NewSite' } }
				]"
			/>
			<div v-if="$resources.upcomingInvoice.data" class="flex flex-wrap">
				<div class="mr-5">
					<strong>{{ $t('account_balance') }}: </strong
					>{{
						this.$formatMoney(
							$resources.upcomingInvoice.data?.available_credits?.amount_all,
							0
						)
					}}
					VND
				</div>
				<div>
					<strong>{{ $t('available_balance') }}: </strong
					>{{
						this.$formatMoney(
							$resources.upcomingInvoice.data?.available_balances,
							0
						)
					}}
					VND
				</div>
			</div>
			<Button
				v-if="$resources.upcomingInvoice.loading"
				:loading="true"
				:loadingText="$t('loading')"
			/>
		</header>
		<WizardCard>
			<div class="mb-2 text-center">
				<h1 class="text-2xl font-bold">{{ $t('New_Site') }}</h1>
				<p v-if="benchTitle" class="text-base text-gray-700">
					{{ $t('NewSite_content_4') }}
					<span class="font-medium">{{ benchTitle }}</span>
				</p>
			</div>
			<Steps :steps="steps">
				<template
					v-slot="{ active: activeStep, next, previous, hasPrevious, hasNext }"
				>
					<div class="mt-8"></div>
					<Hostname
						v-model:checkRestore="checkRestore"
						v-show="activeStep.name === 'Hostname'"
						v-model="subdomain"
						@error="error => (subdomainValid = !Boolean(error))"
					/>
					<Apps
						v-show="activeStep.name === 'Apps'"
						:privateBench="privateBench"
						:bench="benchName"
						v-model:appsDefault="appsDefault"
						v-model:selectedApps="selectedApps"
						v-model:selectedGroup="selectedGroup"
						v-model:selectedRegion="selectedRegion"
						v-model:shareDetailsConsent="shareDetailsConsent"
					/>

					<div v-if="activeStep.name === 'Select App Plans'">
						<ChangeAppPlanSelector
							v-for="app in appsWithPlans"
							:key="app.name"
							:app="app.name"
							:group="selectedGroup"
							:currentPlan="selectedAppPlans[app.name]"
							:editable="false"
							class="mb-9"
							@change="plan => (selectedAppPlans[app.name] = plan.name)"
							v-model:appPlans="appPlans"
						/>
					</div>

					<SiteSummaryBilling
						:detail="{
							subdomain: subdomain,
							selectedApps: selectedApps,
							selectedPlan: selectedPlan,
							selectedAppPlans: selectedAppPlans,
							appPlans: appPlans
						}"
						v-model:totalBilling="totalBilling"
						v-show="activeStep.name === 'Summary Invoice'"
					/>

					<Restore
						v-model:selectedFiles="selectedFiles"
						v-model:skipFailingPatches="skipFailingPatches"
						v-show="activeStep.name == 'Restore'"
					/>
					<Plans
						v-model:selectedPlan="selectedPlan"
						:bench="bench"
						:pointPlanSite="pointPlanSite"
						:benchTeam="benchTeam"
						v-show="activeStep.name === 'Plan'"
					/>
					<ErrorMessage class="mt-2" :message="validationMessage" />
					<div class="mt-4">
						<!-- Region consent checkbox -->
						<div class="my-6 flex w-full" v-if="!hasNext">
							<FormControl
								id="policy"
								name="policy"
								type="checkbox"
								v-model="agreedToRegionConsent"
								label=""
							/>
							<label class="ml-2 text-base" for="policy">
								{{ $t('NewServer_content_1') }}
								<Link
									class="border-none"
									href="https://eov.mbwcloud.com/privacy"
									target="_blank"
									><span class="text-blue-500 hover:text-blue-700">
										{{ $t('Privacy_Policy') }}
									</span></Link
								>
								{{ $t('of_EOVCloud') }}
							</label>
						</div>

						<ErrorMessage class="mb-4" :message="$resources.newSite.error" />

						<div class="flex items-center justify-between">
							<Button v-show="hasPrevious" @click="previous">
								{{ $t('Back') }}
							</Button>
							<Button
								v-show="
									(activeStep.name !== 'Restore' || wantsToRestore) && hasNext
								"
								class="ml-auto"
								variant="solid"
								@click="nextStep(activeStep, next)"
								:class="{ 'mt-2': hasPrevious }"
								:loading="loadingPlans"
								:loadingText="$t('loading')"
							>
								{{ $t('Next') }}
							</Button>
							<Button
								v-show="
									!wantsToRestore && activeStep.name === 'Restore' && hasNext
								"
								class="ml-auto"
								variant="solid"
								@click="nextStep(activeStep, next)"
							>
								{{ $t('Skip') }}
							</Button>
							<Button
								v-show="!hasNext"
								class="ml-auto"
								variant="solid"
								:class="{ 'mt-2': hasPrevious }"
								@click="handleCreateSite"
								:loading="$resources.newSite.loading"
							>
								{{ $t('Create_site') }}
							</Button>
						</div>
					</div>
				</template>
			</Steps>
		</WizardCard>
	</div>
</template>

<script>
import WizardCard from '@/components/WizardCard.vue';
import Steps from '@/components/Steps.vue';
import Hostname from './NewSiteHostname.vue';
import Apps from './NewSiteApps.vue';
import Restore from './NewSiteRestore.vue';
import Plans from './NewSitePlans.vue';
import SiteSummaryBilling from './SiteSummaryBilling.vue';
import ChangeAppPlanSelector from '@/components/ChangeAppPlanSelector.vue';

export default {
	name: 'NewSite',
	props: ['bench'],
	components: {
		WizardCard,
		Steps,
		Hostname,
		Apps,
		Restore,
		Plans,
		SiteSummaryBilling,
		ChangeAppPlanSelector
	},
	data() {
		return {
			subdomain: null,
			subdomainValid: false,
			totalBilling: 0,
			checkRestore: 'new',
			pointPlanSite: 0,
			billingDetails: {},
			privateBench: false,
			benchName: null,
			benchTitle: null,
			benchTeam: null,
			selectedApps: [],
			appsDefault: [],
			selectedGroup: null,
			selectedRegion: null,
			selectedFiles: {
				database: null,
				public: null,
				private: null
			},
			skipFailingPatches: false,
			selectedPlan: null,
			shareDetailsConsent: false,
			validationMessage: null,
			steps: [
				{
					name: 'Hostname',
					validate: () => {
						return this.subdomainValid;
					}
				},
				{
					name: 'Apps',
					validate: () => {
						if (this.privateBench) return true;
						if (!this.selectedRegion) {
							this.validationMessage = this.$t('Please_select_the_region');
							return false;
						} else {
							this.validationMessage = null;
						}
						return true;
					}
				},
				{
					name: 'Plan'
				},
				{
					name: 'Summary Invoice'
				}
			],
			agreedToRegionConsent: false,
			selectedAppPlans: {},
			appPlans: [],
			loadingPlans: false,
			infoBench: null
		};
	},
	async mounted() {
		this.$socket.on('balance_updated', () => {
			setTimeout(() => {
				this.$resources.upcomingInvoice.reset();
				this.$resources.upcomingInvoice.reload();
			}, 1000);
		});

		if (this.$route.query.domain) {
			let domain = this.$route.query.domain.split('.');
			if (domain) {
				this.subdomain = domain[0];
			}
			this.$router.replace({});
		}
		if (this.bench) {
			this.privateBench = true;
			this.selectedGroup = this.bench;
			this.benchTitle = this.bench;
			let { title, creation, team } = await this.$call(
				'press.api.bench.get_title_and_creation',
				{
					name: this.bench
				}
			);
			this.infoBench = { title, creation, team };
			this.benchName = this.bench;
			this.benchTitle = title;
			this.benchTeam = team;
			if (team == this.$account.team.name) {
				// Select a zero cost plan and remove the plan selection step
				this.selectedPlan = { name: 'Unlimited' };
				let plan_step_index = this.steps.findIndex(step => step.name == 'Plan');
				this.steps.splice(plan_step_index, 1);
				plan_step_index = this.steps.findIndex(
					step => step.name == 'Summary Invoice'
				);
				this.steps.splice(plan_step_index, 1);
			}
		}
	},
	resources: {
		upcomingInvoice: { url: 'press.api.billing.upcoming_invoice', auto: true },
		getBillingAddress() {
			return {
				url: 'press.api.account.get_billing_information',
				auto: true,
				onSuccess(data) {
					this.billingDetails = data.billing_details;
				}
			};
		},
		newSite() {
			return {
				url: 'press.api.site.new',
				params: {
					site: {
						name: this.subdomain,
						apps: this.selectedApps,
						group: this.selectedGroup,
						cluster: this.selectedRegion,
						plan: this.selectedPlan ? this.selectedPlan.name : null,
						files: this.selectedFiles,
						share_details_consent: this.shareDetailsConsent,
						skip_failing_patches: this.skipFailingPatches,
						selected_app_plans: this.selectedAppPlans
					},
					lang: this.$i18n.locale
				},
				onSuccess(data) {
					let { site, job = '' } = data;
					this.$router.push(`/sites/${site}/jobs/${job}`);
				},
				async validate() {
					let canCreate =
						this.subdomainValid &&
						this.selectedApps.length > 0 &&
						this.selectedPlan &&
						(!this.wantsToRestore || this.selectedFiles.database);

					if (!this.agreedToRegionConsent) {
						return this.$t('NewSite_content_5');
					}

					if (!this.infoBench) {
						// kiem tra so du
						if (
							this.totalBilling >
							this.$resources.upcomingInvoice.data?.available_balances
						) {
							return this.$t('NewSite_content_6');
						}
					}

					if (!canCreate) {
						return this.$t('NewSite_content_7');
					}
				}
			};
		}
	},
	computed: {
		wantsToRestore() {
			if (this.selectedFiles.database) {
				return true;
			}
			return false;
		}
	},
	watch: {
		checkRestore(value) {
			const appsStepIndex = this.steps.findIndex(step => step.name == 'Apps');
			const selectAppPlansStepIndex = this.steps.findIndex(
				step => step.name == 'Select App Plans'
			);
			const restoreStepIndex = this.steps.findIndex(
				step => step.name == 'Restore'
			);

			if (value == 'new') {
				if (restoreStepIndex >= 0) {
					this.steps.splice(restoreStepIndex, 1);
				}
			} else if (restoreStepIndex < 0) {
				if (selectAppPlansStepIndex >= 0) {
					this.steps.splice(selectAppPlansStepIndex + 1, 0, {
						name: 'Restore'
					});
				} else {
					this.steps.splice(appsStepIndex + 1, 0, {
						name: 'Restore'
					});
				}
			}
		}
	},
	methods: {
		handleCreateSite() {
			// Xoa goi khi loai bo app
			let appPlans = this.selectedAppPlans;
			let apps = Object.keys(appPlans);
			apps.forEach(el => {
				if (!this.selectedApps.includes(el)) {
					delete appPlans[el];
				}
			});
			this.selectedAppPlans = appPlans;

			// tao site
			this.$resources.newSite.submit();
		},
		async nextStep(activeStep, next) {
			if (activeStep.name == 'Hostname') {
				this.validationMessage = '';
				if (!this.subdomain) {
					this.validationMessage = this.$t('NewSite_content_8');
				}
			}
			// lay ti le su dung cho plan
			let trongSoApp = {};
			this.appsDefault.forEach(app => {
				trongSoApp[app.app] = app.trong_so || 0;
			});
			let newPoind = this.billingDetails.number_of_employees || 0;
			this.selectedApps.forEach(el => {
				newPoind *= trongSoApp[el] || 0;
			});
			this.pointPlanSite = newPoind;
			//

			if (activeStep.name == 'Apps') {
				this.loadingPlans = true;

				// Fetch apps that have plans
				this.appsWithPlans = await this.$call(
					'press.api.marketplace.get_apps_with_plans',
					{
						apps: JSON.stringify(this.selectedApps),
						release_group: this.selectedGroup
					}
				);

				if (this.appsWithPlans && this.appsWithPlans.length > 0) {
					this.addPlanSelectionStep();

					// loại bỏ refresh select plan
					// this.selectedAppPlans = {};
					// for (let app of this.appsWithPlans) {
					// 	this.selectedAppPlans[app.name] = null;
					// }
				} else {
					this.validationMessage = null;
					this.removePlanSelectionStepIfExists();
				}

				this.loadingPlans = false;
			}

			next();
		},
		addPlanSelectionStep() {
			const appsStepIndex = this.steps.findIndex(step => step.name == 'Apps');

			const selectAppPlansStepIndex = this.steps.findIndex(
				step => step.name == 'Select App Plans'
			);
			if (selectAppPlansStepIndex < 0) {
				this.steps.splice(appsStepIndex + 1, 0, {
					name: 'Select App Plans',
					validate: () => {
						for (let app of Object.keys(this.selectedAppPlans)) {
							if (!this.selectedAppPlans[app]) {
								this.validationMessage = `${this.$t(
									'NewSite_content_9'
								)} ${app}`;
								return false;
							} else {
								this.validationMessage = null;
							}
						}

						return true;
					}
				});
			}
		},
		removePlanSelectionStepIfExists() {
			const selectAppPlansStepIndex = this.steps.findIndex(
				step => step.name == 'Select App Plans'
			);
			if (selectAppPlansStepIndex >= 0) {
				this.steps.splice(selectAppPlansStepIndex, 1);
			}
		}
	}
};
</script>
