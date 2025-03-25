<template>
	<div>
		<div v-if="$resources.versions.loading" class="flex justify-center">
			<LoadingText />
		</div>
		<div class="space-y-6" v-if="$resources.versions.data">
			<div v-if="!this.privateBench">
				<h2 class="text-lg font-semibold">
					{{ $t('Select_a_Frappe_version') }}
				</h2>
				<p class="text-base text-gray-700">
					{{ $t('NewSiteApps_content_1') }}
				</p>
				<div class="mt-4">
					<FormControl
						type="select"
						v-model="selectedVersion"
						:options="versionOptions"
					/>
				</div>
			</div>
			<div v-if="regionOptions.length > 0">
				<h2 class="text-lg font-semibold">{{ $t('Select_Region') }}</h2>
				<p class="text-base text-gray-700">
					{{ $t('NewSiteApps_content_2') }}
				</p>
				<div class="mt-4">
					<RichSelect
						:value="selectedRegion"
						@change="$emit('update:selectedRegion', $event)"
						:options="regionOptions"
					/>
				</div>
			</div>
			<div
				v-if="publicApps.length > 1 || privateApps.length || featureApp.length"
			>
				<h2 class="text-lg font-semibold">
					{{ $t('Select_apps_to_install') }}
				</h2>
				<p class="text-base text-gray-700">
					{{ $t('NewSiteApps_content_3') }}
				</p>
				<div class="mt-4 space-y-4">
					<div v-if="featureApp.length > 0">
						<h3 class="text-sm font-medium">
							{{ $t('NewSiteApps_content_4') }}
						</h3>
						<div
							class="-mx-2 mt-1 grid max-h-56 grid-cols-2 gap-4 overflow-y-auto px-2 py-2"
						>
							<SelectableCard
								v-for="publicApp in featureApp"
								:key="publicApp.app"
								@click.native="toggleApp(publicApp)"
								:title="
									publicApp.marketplace
										? publicApp.marketplace.title
										: publicApp.app_title
								"
								:image="
									publicApp.marketplace ? publicApp.marketplace.image : null
								"
								:selected="selectedApps.includes(publicApp.app)"
								v-show="!publicApp.frappe"
								fullCircleImage
							>
								<template #secondary-content>
									<a
										v-if="publicApp.marketplace"
										class="inline-block text-sm leading-snug text-gray-600"
										:href="'/' + publicApp.marketplace.route"
										target="_blank"
										@click.stop
									>
										{{ $t('Details') }}
									</a>
									<span class="text-sm leading-snug text-gray-700" v-else>
										{{ publicApp.repository_owner }}/{{ publicApp.repository }}
									</span>
								</template>
							</SelectableCard>
							<div class="h-1 py-4" v-if="featureApp.length > 4"></div>
						</div>
					</div>
					<div v-if="privateApps.length > 0">
						<h3 class="text-sm font-medium">{{ $t('Your_Private_Apps') }}</h3>
						<div
							class="-mx-2 mt-1 grid max-h-56 grid-cols-2 gap-4 overflow-y-auto px-2 py-2"
						>
							<SelectableCard
								v-for="app in privateApps"
								:key="app.app"
								@click.native="toggleApp(app)"
								:selected="selectedApps.includes(app.app)"
								:title="app.app_title"
								fullCircleImage
							>
								<div slot="secondary-content" class="text-base text-gray-700">
									{{ app.repository_owner }}:{{ app.branch }}
								</div>
							</SelectableCard>
						</div>
					</div>
					<div
						v-if="
							publicApps.length > 1 &&
							(featureApp.length > 0 || privateApps.length > 0)
						"
						class="flex justify-end"
					>
						<Button
							:variant="'ghost'"
							theme="gray"
							size="sm"
							label="Button"
							:loading="false"
							:loadingText="null"
							:disabled="false"
							:link="null"
							@click="() => (this.showMore = !this.showMore)"
						>
							<div class="text-sm font-medium text-gray-700 underline">
								{{ this.showMore ? $t('View_all') : $t('Hide_more') }}
							</div>
						</Button>
					</div>
					<div
						v-if="publicApps.length"
						:class="{
							hidden:
								featureApp.length < 1 && privateApps.length < 1
									? false
									: showMore
						}"
					>
						<h3 class="text-sm font-medium">{{ $t('All_applications') }}</h3>
						<div
							class="-mx-2 mt-1 grid max-h-56 grid-cols-2 gap-4 overflow-y-auto px-2 py-2"
						>
							<SelectableCard
								v-for="publicApp in publicApps"
								:key="publicApp.app"
								@click.native="toggleApp(publicApp)"
								:title="
									publicApp.marketplace
										? publicApp.marketplace.title
										: publicApp.app_title
								"
								:image="
									publicApp.marketplace ? publicApp.marketplace.image : null
								"
								:selected="selectedApps.includes(publicApp.app)"
								v-show="!publicApp.frappe"
								fullCircleImage
							>
								<template #secondary-content>
									<a
										v-if="publicApp.marketplace"
										class="inline-block text-sm leading-snug text-gray-600"
										:href="'/' + publicApp.marketplace.route"
										target="_blank"
										@click.stop
									>
										{{ $t('Details') }}
									</a>
									<span class="text-sm leading-snug text-gray-700" v-else>
										{{ publicApp.repository_owner }}/{{ publicApp.repository }}
									</span>
								</template>
							</SelectableCard>
							<div class="h-1 py-4" v-if="publicApps.length > 4"></div>
						</div>
					</div>
				</div>
			</div>
			<div class="flex" v-if="selectedApps.includes('erpnext')">
				<FormControl
					id="term"
					name="term"
					type="checkbox"
					label=""
					@change="
						val => $emit('update:shareDetailsConsent', val.target.checked)
					"
				/>
				<label class="ml-2 text-base" for="term">
					{{ $t('NewServer_content_1') }}
					<Link
						class="border-none"
						href="https://support.eov.solutions"
						target="_blank"
						><span class="text-blue-500 hover:text-blue-700"
							>{{ $t('NewServer_content_2') }}
						</span></Link
					>
					{{ $t('of_EOVCloud') }}
				</label>
			</div>
		</div>
	</div>
</template>
<script>
import SelectableCard from '@/components/SelectableCard.vue';
import RichSelect from '@/components/RichSelect.vue';

export default {
	components: {
		SelectableCard,
		RichSelect
	},
	name: 'Apps',
	emits: [
		'update:appsDefault',
		'update:selectedApps',
		'update:selectedGroup',
		'update:selectedRegion',
		'update:shareDetailsConsent'
	],
	props: [
		'appsDefault',
		'selectedApps',
		'selectedGroup',
		'privateBench',
		'selectedRegion',
		'shareDetailsConsent',
		'bench'
	],
	data() {
		return {
			selectedVersion: null,
			version: null,
			showMore: true
		};
	},
	computed: {
		featureApp() {
			let arr_app = this.marketplaceAppsFeature.map(el => el.app);
			return this.apps
				.filter(app => app.public && arr_app.includes(app.app))
				.map(app => {
					app.marketplace = this.marketplaceApps[app.app] || null;
					return app;
				});
		},
		publicApps() {
			let arr_app = this.marketplaceAppsFeature.map(el => el.app);
			return this.apps
				.filter(app => app.public && !arr_app.includes(app.app))
				.map(app => {
					app.marketplace = this.marketplaceApps[app.app] || null;
					return app;
				});
		},
		privateApps() {
			return this.apps.filter(app => !app.public);
		},
		apps() {
			let group = this.getSelectedGroup();
			return group ? group.apps : [];
		},
		versionOptions() {
			return this.versions.map(version => version.name);
		},
		regionOptions() {
			let group = this.getSelectedGroup();
			return group
				? group.clusters.map(d => ({
						label: d.title,
						value: d.name,
						image: d.image
				  }))
				: [];
		}
	},
	watch: {
		selectedVersion(value) {
			if (!this.privateBench) {
				let selectedVersion = this.versions.find(v => v.name == value);
				this.$emit('update:selectedGroup', selectedVersion?.group?.name);
			}
		},
		selectedGroup() {
			this.$emit('update:selectedApps', ['frappe']);
			if (this.regionOptions.length > 0) {
				this.$emit('update:selectedRegion', this.regionOptions[0].value);
			}
		}
	},
	methods: {
		toggleApp(app) {
			if (app.frappe) return;
			if (!this.selectedApps.includes(app.app)) {
				this.$emit('update:selectedApps', this.selectedApps.concat(app.app));
			} else {
				this.$emit(
					'update:selectedApps',
					this.selectedApps.filter(a => a !== app.app)
				);
			}
		},
		getSelectedGroup() {
			if (!this.versions || !this.selectedVersion || !this.selectedGroup) {
				return null;
			}
			let selectedVersion = this.versions.find(
				v => v.name == this.selectedVersion
			);
			return selectedVersion?.group;
		}
	},
	resources: {
		versions() {
			return {
				url: 'press.api.site.get_new_site_options',
				auto: true,
				params: {
					group: this.privateBench ? this.bench : ''
				},
				onSuccess(r) {
					this.versions = r.versions.filter(v => {
						return v?.group;
					});
					this.marketplaceApps = r.marketplace_apps;
					this.marketplaceAppsFeature = r.marketplace_apps_feature;

					// from mounted
					if (this.privateBench) {
						this.selectedVersion = this.versions.filter(
							v => v?.group.name === this.bench
						)[0]?.name;
						this.$emit('update:selectedApps', ['frappe']);
					} else {
						this.selectedVersion = this.versions[0]?.name;
					}

					if (this.regionOptions.length == 1) {
						this.$emit('update:selectedRegion', this.regionOptions[0].value);
					}

					let selectedVersion = this.versions.find(
						v => v.name == this.selectedVersion
					);
					if (selectedVersion?.group) {
						this.$emit('update:appsDefault', selectedVersion?.group.apps);
					}
				}
			};
		}
	}
};
</script>
