<template>
	<WizardCard>
		<div>
			<div class="mb-6 text-center">
				<h1 class="text-2xl font-bold sm:text-center">Bench mới</h1>
				<p v-if="serverTitle" class="text-base text-gray-700">
					Bench sẽ được tạo trên máy chủ
					<span class="font-medium">{{ serverTitle.slice(0, -14) }}</span>
				</p>
			</div>
			<div v-if="$resources.options.loading" class="flex justify-center">
				<LoadingText />
			</div>
			<div class="space-y-8 sm:space-y-6" v-else>
				<div>
					<label class="text-lg font-semibold">
						Chọn một tên cho Bench của bạn
					</label>
					<p class="text-base text-gray-700">
						Đặt tên cho bench dựa trên mục đích của nó. Ví dụ, Websites Cá nhân,
						Bench Staging, v.v.
					</p>
					<FormControl class="mt-2" v-model="benchTitle" />
				</div>
				<div v-if="regionOptions.length > 0">
					<h2 class="text-lg font-semibold">Chọn Khu vực</h2>
					<p class="text-base text-gray-700">
						Chọn khu vực trung tâm dữ liệu nơi Bench của bạn sẽ được tạo
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
					<label class="text-lg font-semibold"> Chọn phiên bản Frappe </label>
					<p class="text-base text-gray-700">
						Chọn phiên bản Frappe cho Bench của bạn.
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
						Chọn ứng dụng để cài đặt
					</label>
					<p class="text-base text-gray-700">
						Những ứng dụng này sẽ có sẵn cho các trang web trên Bench của bạn.
						Bạn cũng có thể thêm ứng dụng vào Bench của bạn sau này.
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
						Tôi đồng ý rằng các luật pháp của khu vực được tôi chọn sẽ áp dụng
						đối với tôi và Frappe.
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
						Tạo Bench
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
					}
				},
				validate() {
					if (!this.benchTitle) {
						return 'Tiêu đề Bench không thể để trống';
					}
					if (!this.selectedVersionName) {
						return 'Chọn một phiên bản để tạo Bench';
					}
					if (this.selectedApps.length < 1) {
						return 'Chọn ít nhất một ứng dụng để tạo Bench';
					}

					if (!this.agreedToRegionConsent) {
						document.getElementById('region-consent').focus();
						return 'Vui lòng đồng ý với sự đồng thuận trên để tạo Bench';
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
