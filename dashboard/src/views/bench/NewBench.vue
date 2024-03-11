<template>
	<WizardCard>
		<div>
			<div class="mb-6 text-center">
				<h1 class="text-2xl font-bold sm:text-center">{{ $t('New_Bench') }}</h1>
				<p v-if="serverTitle" class="text-base text-gray-700">
					{{ $t('Bench_will_be_created_on_server') }}
					<span class="font-medium">{{ serverTitle.slice(0, -14) }}</span>
				</p>
			</div>
			<div v-if="$resources.options.loading" class="flex justify-center">
				<LoadingText />
			</div>
			<div class="space-y-8 sm:space-y-6" v-else>
				<div>
					<label class="text-lg font-semibold">
						{{ $t('Choose_a_name_for_your_bench') }}
					</label>
					<p class="text-base text-gray-700">
						{{ $t('NewBench_content_1') }}
					</p>
					<FormControl class="mt-2" v-model="benchTitle" />
				</div>
				<div v-if="regionOptions.length > 0">
					<h2 class="text-lg font-semibold">{{ $t('Select_Region') }}</h2>
					<p class="text-base text-gray-700">
						{{ $t('NewBench_content_2') }}
					</p>
					<div class="mt-2">
						<RichSelect
							:value="selectedRegion"
							@change="selectedRegion = $event"
							:options="regionOptions"
						/>
					</div>
				</div>
				<div>
					<label class="text-lg font-semibold">
						{{ $t('Select_a_Frappe_version') }}
					</label>
					<p class="text-base text-gray-700">
						{{ $t('NewBench_content_3') }}
					</p>
					<FormControl
						class="mt-2"
						type="select"
						v-model="selectedVersionName"
						:options="versionOptions"
					/>
				</div>

				<div v-if="selectedVersionName">
					<label class="text-lg font-semibold">
						{{ $t('Select_apps_to_install') }}
					</label>
					<p class="text-base text-gray-700">
						{{ $t('NewBench_content_4') }}
					</p>
					<div class="mt-4">
						<AppSourceSelector
							:apps="selectedVersion.apps"
							v-model="selectedApps"
							:multiple="true"
						/>
					</div>
				</div>
				<!-- Region consent checkbox -->
				<div class="my-6">
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
						{{ $t('NewSite_content_1') }}
					</label>
				</div>

				<div class="flex justify-between">
					<ErrorMessage class="mb-2" :message="$resources.createBench.error" />
					<Button
						variant="solid"
						class="ml-auto"
						:loading="$resources.createBench.loading"
						@click="$resources.createBench.submit()"
					>
						{{ $t('Create_Bench') }}
					</Button>
				</div>
			</div>
		</div>
	</WizardCard>
</template>

<script>
import WizardCard from '@/components/WizardCard.vue';
import AppSourceSelector from '@/components/AppSourceSelector.vue';
import RichSelect from '@/components/RichSelect.vue';
export default {
	name: 'NewBench',
	props: ['saas_app', 'server'],
	components: {
		WizardCard,
		AppSourceSelector,
		RichSelect
	},
	data() {
		return {
			benchTitle: null,
			selectedVersionName: null,
			selectedApps: [],
			selectedRegion: null,
			serverTitle: null,
			agreedToRegionConsent: false
		};
	},
	resources: {
		options() {
			return {
				url: 'press.api.bench.options',
				initialData: {
					versions: [],
					clusters: []
				},
				auto: true,
				onSuccess(options) {
					if (!this.selectedVersionName) {
						this.selectedVersionName = options.versions[0].name;
					}
					if (!this.selectedRegion) {
						this.selectedRegion = this.options.clusters[0].name;
					}
				}
			};
		},
		createBench() {
			return {
				url: 'press.api.bench.new',
				params: {
					bench: {
						title: this.benchTitle,
						version: this.selectedVersionName,
						cluster: this.selectedRegion,
						saas_app: this.saas_app || null,
						apps: this.selectedApps.map(app => ({
							name: app.app,
							source: app.source.name
						})),
						server: this.server || null
					},
					lang: this.$i18n.locale
				},
				validate() {
					if (!this.benchTitle) {
						return this.$t('NewBench_content_5');
					}
					if (!this.selectedVersionName) {
						return this.$t('NewBench_content_6');
					}
					if (this.selectedApps.length < 1) {
						return this.$t('NewBench_content_7');
					}

					if (!this.agreedToRegionConsent) {
						document.getElementById('region-consent').focus();
						return this.$t('NewBench_content_8');
					}
				},
				onSuccess(benchName) {
					this.$router.push(`/benches/${benchName}`);
				}
			};
		}
	},
	async mounted() {
		if (this.server) {
			let { title, cluster } = await this.$call(
				'press.api.server.get_title_and_cluster',
				{
					name: this.server
				}
			);
			this.serverTitle = title;
			this.selectedRegion = cluster;
		}
	},
	watch: {
		selectedVersionName() {
			this.$nextTick(() => {
				let frappeApp = this.getFrappeApp(this.selectedVersion.apps);
				this.selectedApps = [{ app: frappeApp.name, source: frappeApp.source }];
			});
		},
		selectedApps: {
			handler(newVal, oldVal) {
				// dont remove frappe app
				let hasFrappe = newVal.find(app => app.app === 'frappe');
				if (!hasFrappe && oldVal) {
					this.selectedApps = oldVal;
				}
			},
			deep: true
		}
	},
	methods: {
		getFrappeApp(apps) {
			return apps.find(app => app.name === 'frappe');
		}
	},
	computed: {
		options() {
			return this.$resources.options.data;
		},
		selectedVersion() {
			return this.options.versions.find(
				v => v.name === this.selectedVersionName
			);
		},
		versionOptions() {
			return this.options.versions.map(v => ({
				label: `${v.name} (${v.status})`,
				value: v.name
			}));
		},
		regionOptions() {
			let clusters = this.options.clusters;
			if (this.server && this.selectedRegion) {
				clusters = clusters.filter(
					cluster => cluster.name === this.selectedRegion
				);
			}
			return clusters.map(d => ({
				label: d.title,
				value: d.name,
				image: d.image
			}));
		}
	}
};
</script>
