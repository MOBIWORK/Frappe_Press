<template>
	<WizardCard v-if="options">
		<div class="mb-6 text-center">
			<h1 class="text-2xl font-bold">{{ $t('Create_a_new_server') }}</h1>
		</div>
		<Steps :steps="steps">
			<template
				v-slot="{ active: activeStep, next, previous, hasPrevious, hasNext }"
			>
				<div class="mt-8"></div>
				<Hostname
					:options="options"
					v-show="activeStep.name === 'Hostname'"
					v-model:title="title"
					v-model:selectedRegion="selectedRegion"
				/>
				<AppServerPlans
					v-model:selectedAppPlan="selectedAppPlan"
					:options="options"
					:selectedRegion="selectedRegion"
					v-show="activeStep.name === 'AppServerPlan'"
				/>
				<DBServerPlans
					v-model:selectedDBPlan="selectedDBPlan"
					:options="options"
					:selectedRegion="selectedRegion"
					v-show="activeStep.name === 'DBServerPlan'"
				/>
				<VerifyServer
					:options="options"
					:selectedAppPlan="selectedAppPlan"
					:selectedDBPlan="selectedDBPlan"
					v-show="activeStep.name === 'VerifyServer'"
				/>
				<ErrorMessage :message="validationMessage" />
				<div class="mt-4">
					<!-- Region consent checkbox -->
					<div class="my-6" v-if="!hasNext">
						<input
							id="region-consent"
							type="checkbox"
							class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
							v-model="agreedToRegionConsent"
						/>
						<label
							for="region-consent"
							class="ml-1 text-sm font-semibold text-gray-900"
						>
							{{ $t('NewServer_content_1') }}
							<Link
								class="border-none"
								href="/thoa-thuan-su-dung-dich-vu"
								target="_blank"
								><span class="text-blue-500 hover:text-blue-700"
									>{{ $t('NewServer_content_2') }}
								</span></Link
							>.
						</label>
					</div>

					<ErrorMessage class="mb-4" :message="$resources.newServer.error" />

					<div class="flex justify-between">
						<Button v-if="hasPrevious" @click="previous">
							{{ $t('Back') }}
						</Button>
						<Button
							v-if="hasNext"
							class="ml-auto"
							variant="solid"
							@click="nextStep(activeStep, next)"
							:class="{ 'mt-2': hasPrevious }"
						>
							{{ $t('Next') }}
						</Button>
						<Button
							v-show="!hasNext"
							variant="solid"
							class="ml-auto"
							@click="$resources.newServer.submit()"
							:loading="$resources.newServer.loading"
						>
							{{ $t('Create_Servers') }}
						</Button>
					</div>
				</div>
			</template>
		</Steps>
	</WizardCard>
</template>

<script>
import WizardCard from '@/components/WizardCard.vue';
import Steps from '@/components/Steps.vue';
import Hostname from './NewServerHostname.vue';
import AppServerPlans from './NewAppServerPlans.vue';
import DBServerPlans from './NewDBServerPlans.vue';
import VerifyServer from './NewVerifyServer.vue';

export default {
	name: 'NewServer',
	components: {
		WizardCard,
		Steps,
		Hostname,
		AppServerPlans,
		DBServerPlans,
		VerifyServer
	},
	data() {
		return {
			title: null,
			options: null,
			selectedRegion: null,
			selectedAppPlan: null,
			selectedDBPlan: null,
			validationMessage: null,
			steps: [
				{
					name: 'Hostname',
					validate: () => {
						return this.title && this.selectedRegion;
					}
				},
				{
					name: 'AppServerPlan',
					validate: () => {
						return this.selectedAppPlan;
					}
				},
				{
					name: 'DBServerPlan',
					validate: () => {
						return this.selectedDBPlan;
					}
				},
				{
					name: 'VerifyServer'
				}
			],
			agreedToRegionConsent: false
		};
	},
	async mounted() {
		this.options = await this.$call('press.api.server.options', {
			lang: this.$i18n.locale
		});
		this.options.app_plans = this.options.app_plans.map(plan => {
			plan.disabled = !this.$account.hasBillingInfo;
			return plan;
		});
		this.options.db_plans = this.options.db_plans.map(plan => {
			plan.disabled = !this.$account.hasBillingInfo;
			return plan;
		});
	},
	resources: {
		newServer() {
			return {
				url: 'press.api.server.new',
				params: {
					server: {
						title: this.title,
						cluster: this.selectedRegion,
						app_plan: this.selectedAppPlan?.name,
						db_plan: this.selectedDBPlan?.name
					},
					lang: this.$i18n.locale
				},
				onSuccess(data) {
					let { server } = data;
					this.$router.push(`/servers/${server}/install`);
				},
				validate() {
					let canCreate =
						this.title &&
						this.selectedAppPlan &&
						this.selectedDBPlan &&
						this.selectedRegion;

					if (!this.selectedAppPlan) {
						return this.$t('NewServer_content_3');
					}

					if (!this.selectedDBPlan) {
						return this.$t('NewServer_content_4');
					}

					if (!this.selectedRegion) {
						return this.$t('NewServer_content_5');
					}

					if (!this.agreedToRegionConsent) {
						document.getElementById('region-consent').focus();

						return this.$t('NewServer_content_6');
					}

					if (!canCreate) {
						return this.$t('NewServer_content_7');
					}
				}
			};
		}
	},
	computed: {},
	methods: {
		async nextStep(activeStep, next) {
			next();
		}
	}
};
</script>
