<template>
	<div class="grid min-h-screen grid-cols-1 md:grid-cols-2">
		<!-- Left Column: Background and Logo -->
		<div class="col-span-1 hidden h-screen bg-gray-50 md:flex">
			<div v-if="saasProduct" class="relative h-screen w-full overflow-hidden">
				<!-- Background Image -->
				<img :src="saasProduct?.background" alt="Background" class="h-full w-full object-contain" />

				<!-- Logo on top -->
			</div>

			<div v-else class="relative h-screen w-full overflow-hidden">
				<!-- Background Image -->
				<img src="/public/bg1.png" alt="Background" class="h-full w-full object-contain" />

				<!-- Logo on top -->
				<div class="absolute left-8 top-8 z-10">
					<FCLogo class="h-16 w-auto drop-shadow-lg transition-all duration-300 hover:drop-shadow-xl" />
				</div>
			</div>
		</div>

		<!-- Right Column: Site Setup Form -->
		<div
			class="relative col-span-1 flex h-full w-full items-center justify-center py-8 md:overflow-auto md:bg-white">
			<LoginBox :title="__('Set up your site')" :subtitle="__('Enter site name to set up your site')"
				class="w-full h-full md:h-auto md:max-w-md transition-all duration-300 shadow-xl rounded-xl">
				<template v-slot:logo v-if="saasProduct">
					<div class="flex mb-4 w-full justify-center">
						<img class="h-16 w-auto rounded-md shadow-md transition-all duration-300 hover:shadow-lg"
							:src="saasProduct?.logo" alt="Product Logo" />
					</div>
				</template>

				<form class="mt-6 flex flex-col space-y-4 w-full" @submit.prevent="createSite">
					<div class="w-full space-y-1.5">
						<div class="flex items-center gap-2">
							<label class="block text-xs text-ink-gray-5"> {{ __('Site name') }} </label>
							<Tooltip text="You will be able to access your site via your site name">
								<i-lucide-info class="h-4 w-4 text-gray-500" />
							</Tooltip>
						</div>
						<div class="col-span-2 flex w-full">
							<input
								class="dark:[color-scheme:dark] z-10 h-9 w-full rounded rounded-r-none border border-outline-gray-2 bg-surface-white py-1.5 pl-3 pr-2 text-base text-ink-gray-8 placeholder-ink-gray-4 transition-all duration-300 hover:border-outline-gray-3 hover:shadow-sm focus:border-outline-gray-4 focus:bg-surface-white focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3"
								:placeholder="saasProduct ? `${saasProduct?.name}-site` : 'company-name'"
								v-model="subdomain" />
							<div
								class="flex cursor-default items-center rounded-r border-y border-r border-outline-gray-2 bg-gray-50 px-3 text-base">
								<!-- .{{ domain }} -->
								 .nhansu360.com
							</div>
						</div>
						<div class="mt-2">
							<div v-if="$resources.subdomainExists.loading" class="text-sm text-gray-600">
								Checking...
							</div>
							<template v-else-if="!$resources.subdomainExists.error &&
								$resources.subdomainExists.fetched &&
								subdomain
							">
								<div v-if="$resources.subdomainExists.data"
									class="text-sm text-green-600 flex items-center gap-1">
									<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none"
										viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
											d="M5 13l4 4L19 7" />
									</svg>
									<!-- {{ subdomain }}.{{ domain }} {{ __('is available') }} -->
									{{ subdomain }}.nhansu360.com {{ __('is available') }}
								</div>
								<div v-else class="text-sm text-red-600 flex items-center gap-1">
									<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none"
										viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
											d="M6 18L18 6M6 6l12 12" />
									</svg>
									<!-- {{ subdomain }}.{{ domain }} {{ __('is not available') }} -->
									{{ subdomain }}.nhansu360.com {{ __('is not available') }}
								</div>
							</template>

							<ErrorMessage :message="$resources.subdomainExists.error" />
						</div>
					</div>
					<ErrorMessage class="mt-2 w-full" :message="$resources.createSite?.error" />
					<Summary v-if="subdomain" :options="siteSummaryOptions" />
					<Button
						class="mt-8 w-full transform transition-all duration-300 hover:shadow-md hover:-translate-y-0.5"
						:disabled="!!$resources.subdomainExists.error ||
							!$resources.subdomainExists.data ||
							!subdomain.length
							" variant="solid" :label="__('Create site')" :loading="findingClosestServer || $resources.createSite?.loading"
						:loadingText="'Creating site...'" />
				</form>

				<!-- Language Selector -->
				<template v-slot:footer>
					<div class="flex items-center justify-center py-4 border-t border-gray-100 mt-6 w-full">
						<SelectLanguage class="w-full opacity-80 hover:opacity-100 transition-opacity duration-300" />
					</div>
				</template>
			</LoginBox>
		</div>
	</div>
</template>
<script>
import { debounce } from 'frappe-ui';
import { toast } from 'vue-sonner';
import { validateSubdomain } from '../../utils/site';
import { DashboardError } from '../../utils/error';
import LoginBox from '../../components/auth/LoginBox.vue';
import dayjs from '../../utils/dayjs';
import SelectLanguage from '../../components/SelectLanguage.vue';
import Summary from '../../components/Summary.vue';

export default {
	name: 'SignupSetup',
	props: ['productId'],
	components: {
		LoginBox,
		SelectLanguage,
		Summary
	},
	data() {
		return {
			progressErrorCount: 0,
			findingClosestServer: false,
			closestCluster: null,
			subdomain: '',
		};
	},
	watch: {
		subdomain: {
			handler: debounce(function () {
				this.$resources.subdomainExists.submit();
			}, 500),
		},
	},
	resources: {
		subdomainExists() {
			return {
				url: 'press.api.site.exists',
				makeParams() {
					return {
						domain: this.domain,
						subdomain: this.subdomain,
					};
				},
				validate() {
					const error = validateSubdomain(this.subdomain);
					if (error) {
						throw new DashboardError(error);
					}
				},
				transform(data) {
					return !Boolean(data);
				},
			};
		},
		siteRequest() {
			return {
				url: 'press.api.product_trial.get_request',
				params: {
					product: this.productId,
					account_request: this.$team.doc.account_request,
				},
				auto: !!this.saasProduct,
				initialData: {},
				onSuccess: (data) => {
					if (data?.status !== 'Pending') {
						this.$router.push({
							name: 'SignupLoginToSite',
							params: { productId: this.productId },
							query: {
								product_trial_request: data.name,
							},
						});
					}
				},
				onError(error) {
					toast.error(error.messages.join('\n'));
				},
			};
		},
		saasProduct() {
			return {
				type: 'document',
				doctype: 'Product Trial',
				name: this.productId,
				auto: true,
			};
		},
		options() {
			return {
				url: 'press.api.site.options_for_new',
				onSuccess(data) {
					console.log("data", data);
					if (data.versions && data.versions.length > 0) {
						this.version = data.versions[0].name;
					}
				},
				auto: true,
			};
		},
		createSite() {
			return {
				url: 'press.api.client.run_doc_method',
				makeParams: () => {
					// Prepare the selected_app_plans object with the plan from the router query or fall back to default
					const planObj = {};

					if (this.selectedPlan) {
						planObj[this.productId] = this.selectedPlan;
					} else {
						planObj[this.productId] = {
							label: "$100.00/mo",
							sublabel: " ",
							name: "MARKETPLACE-PLAN-crm-023",
							title: "Basic3",
							enabled: 1,
							price_inr: 1800,
							price_usd: 100,
							features: [
								{
									value: "5 user",
									icon: "check-circle"
								}
							]
						};
					}

					return {
						dt: 'Product Trial Request',
						dn: this.$resources.siteRequest.data.name,
						method: 'create_site',
						args: {
							subdomain: this.subdomain,
							cluster: this.closestCluster ?? 'Default',
							selected_app_plans: planObj,
						},
					};
				},
				auto: false,
				validate() {
					if (!this.subdomain) {
						throw new DashboardError('Please enter a subdomain');
					}
				},
				onSuccess: (data) => {
					this.$router.push({
						name: 'SignupLoginToSite',
						params: { productId: this.productId },
						query: {
							product_trial_request: this.$resources.siteRequest.data.name,
							subdomain: this.subdomain,
						},
					});
				},
			};
		},
	},
	computed: {
		saasProduct() {
			return this.$resources.saasProduct?.doc;
		},
		domain() {
			return this.saasProduct?.domain;
		},
		options() {
			return this.$resources.options.data
		},
		selectedPlan() {
			try {
				// if (this.$route.query.selected_plan) {
				//     return JSON.parse(this.$route.query.selected_plan);
				// }
				const raw = this.$route.query.selected_plan;
				if (raw) {
					const decoded = decodeURIComponent(raw);
					return JSON.parse(decoded);
				}
			} catch (error) {
				console.error("Error parsing selected plan:", error);
			}
			return null;
		},
		siteSummaryOptions() {

			const appSource = this.options?.app_source_details?.find(
				(app) => app.app === this.productId
			);

			return [
				{
					label: __('Application name'),
					value: appSource.app_title,
				},
				{
					label: __('Site name'),
					// value: `${this.subdomain}.${this.saasProduct?.domain}`,
					value: `${this.subdomain}.nhansu360.com`,
				},
				{
					label: __('Plan name'),
					value: this.selectedPlan.title,
				},
				{
					label: __('Price plan'),
					value: `${this.$format.formatVND(this.selectedPlan.price_vnd)} VNĐ`,
				}
			];
		},
	},
	methods: {
		async createSite() {
			await this.getClosestCluster();
			return this.$resources.createSite.submit();
		},
		async getClosestCluster() {
			if (this.closestCluster) return this.closestCluster;
			let proxyServers = Object.keys(this.saasProduct.proxy_servers);
			if (proxyServers.length > 0) {
				this.findingClosestServer = true;
				let promises = proxyServers.map((server) => this.getPingTime(server));
				let results = await Promise.allSettled(promises);
				let fastestServer = results.reduce((a, b) =>
					a.value.pingTime < b.value.pingTime ? a : b,
				);
				let closestServer = fastestServer.value.server;
				let closestCluster = this.saasProduct.proxy_servers[closestServer];
				if (!this.closestCluster) {
					this.closestCluster = closestCluster;
				}
				this.findingClosestServer = false;
			}
			return this.closestCluster;
		},
		async getPingTime(server) {
			let pingTime = 999999;
			try {
				let t1 = new Date().getTime();
				await fetch(`https://${server}`);
				let t2 = new Date().getTime();
				pingTime = t2 - t1;
			} catch (error) {
				console.warn(error);
			}
			return { server, pingTime };
		},
		redirectToLogin() {
			this.$router.push({
				name: 'Login',
			});
		},
	},
};
</script>
