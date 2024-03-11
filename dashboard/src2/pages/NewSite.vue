<template>
	<div class="sticky top-0 z-10 shrink-0">
		<Header>
			<Breadcrumbs
				:items="[
					{ label: $t('Sites'), route: '/sites' },
					{ label: $t('New_Site'), route: '/sites/new' }
				]"
			/>
		</Header>
	</div>

	<div class="mx-auto max-w-4xl">
		<div v-if="options" class="space-y-12 pb-[50vh] pt-12">
			<div>
				<div class="flex items-center justify-between">
					<h2 class="text-sm font-medium leading-6 text-gray-900">
						{{ $t('Select_Frappe_Framework_Version') }}
					</h2>
				</div>
				<div class="mt-2">
					<div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
						<button
							v-for="v in options.versions"
							:key="v.value"
							:class="[
								version === v.value
									? 'border-gray-900 ring-1 ring-gray-900 hover:bg-gray-100'
									: 'bg-white text-gray-900  hover:bg-gray-50',
								'flex cursor-pointer items-center justify-between rounded border border-gray-400 p-3 text-sm focus:outline-none'
							]"
							@click="version = v.value"
						>
							<span class="font-medium">{{ v.name }} </span>
							<span class="ml-1 text-gray-600">
								{{ v.status }}
							</span>
						</button>
					</div>
				</div>
			</div>
			<div class="flex flex-col" v-if="options.apps.length">
				<h2 class="text-sm font-medium leading-6 text-gray-900">
					{{ $t('Select_Apps') }}
				</h2>
				<div class="mt-2 w-full space-y-2">
					<div class="grid grid-cols-2 gap-3 sm:grid-cols-2">
						<button
							v-for="app in options.apps"
							:key="app.app"
							@click="toggleApp(app)"
							:class="[
								apps.includes(app.app)
									? 'border-gray-900 ring-1 ring-gray-900 hover:bg-gray-100'
									: 'bg-white text-gray-900  hover:bg-gray-50',
								'flex w-full items-start space-x-2 rounded border p-2 text-left text-base text-gray-900'
							]"
						>
							<img :src="app.image" class="h-10 w-10 shrink-0" />
							<div class="w-full">
								<div class="flex w-full items-center justify-between">
									<span class="text-sm font-medium">
										{{ app.label }}
									</span>
									<!-- <Button></Button> -->
									<a
										:href="`/${app.route}`"
										target="_blank"
										title="App details"
									>
										<FeatherIcon name="external-link" class="h-4 w-4" />
									</a>
								</div>
								<div
									class="mt-1 line-clamp-1 overflow-clip text-p-sm text-gray-600"
									:title="app.description"
								>
									{{ app.description }}
								</div>
							</div>
						</button>
					</div>
				</div>
			</div>
			<div class="flex flex-col" v-if="options.clusters.length">
				<h2 class="text-sm font-medium leading-6 text-gray-900">
					{{ $t('Select_Region') }}
				</h2>
				<div class="mt-2 w-full space-y-2">
					<div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
						<button
							v-for="c in options.clusters"
							:key="c.value"
							@click="cluster = c.value"
							:class="[
								cluster === c.value
									? 'border-gray-900 ring-1 ring-gray-900 hover:bg-gray-100'
									: 'bg-white text-gray-900  hover:bg-gray-50',
								'flex w-full items-center rounded border p-3 text-left text-base text-gray-900'
							]"
						>
							<div class="flex w-full items-center space-x-2">
								<img :src="c.image" class="h-5 w-5" />
								<span class="text-sm font-medium">
									{{ c.label }}
								</span>
							</div>
						</button>
					</div>
					<FormControl
						type="checkbox"
						v-model="agreedToRegionConsent"
						:label="$t('NewSite_content_1')"
					/>
				</div>
			</div>
			<div v-if="version && cluster">
				<h2 class="text-sm font-medium leading-6 text-gray-900">
					{{ $t('Choose_Plan') }}
				</h2>
				<div class="mt-2">
					<SitePlansCards v-model="plan" />
				</div>
			</div>
			<div v-if="version && plan && cluster">
				<h2 class="text-sm font-medium leading-6 text-gray-900">
					{{ $t('Choose_Subdomain') }}
				</h2>
				<div class="mt-2 grid grid-cols-2 items-center gap-3 sm:grid-cols-4">
					<div class="col-span-2 flex w-full">
						<TextInput
							class="flex-1 rounded-r-none"
							placeholder="Subdomain"
							v-model="subdomain"
						/>
						<div class="flex items-center rounded-r bg-gray-100 px-4 text-base">
							.{{ options.domain }}
						</div>
					</div>
					<div
						v-if="$resources.subdomainExists.loading"
						class="text-base text-gray-600"
					>
						{{ $t('Checking') }}...
					</div>
				</div>
				<div class="mt-1">
					<ErrorMessage :message="$resources.subdomainExists.error" />
					<template
						v-if="
							!$resources.subdomainExists.error &&
							$resources.subdomainExists.data != null
						"
					>
						<div
							v-if="$resources.subdomainExists.data"
							class="text-sm text-green-600"
						>
							{{ subdomain }}.{{ options.domain }} {{ $t('is_available') }}
						</div>
						<div v-else class="text-sm text-red-600">
							{{ subdomain }}.{{ options.domain }} {{ $t('is_not_available') }}
						</div>
					</template>
				</div>
			</div>
			<div v-if="version && plan" class="flex flex-col space-y-4">
				<FormControl
					type="checkbox"
					:label="$t('NewSite_content_2')"
					@change="val => (this.shareDetailsConsent = val.target.checked)"
				/>
				<ErrorMessage class="my-2" :message="$resources.newSite.error" />
				<Button
					class="w-1/2"
					variant="solid"
					@click="$resources.newSite.submit()"
					:loading="$resources.newSite.loading"
				>
					{{ $t('Create_site') }}
				</Button>
			</div>
		</div>
	</div>
</template>
<script>
import {
	Autocomplete,
	ErrorMessage,
	FeatherIcon,
	FormControl,
	TextInput,
	debounce
} from 'frappe-ui';
import router from '../router';

export default {
	name: 'NewSite',
	components: {
		FormControl,
		TextInput,
		Autocomplete,
		FeatherIcon,
		ErrorMessage
	},
	data() {
		return {
			show: true,
			subdomain: '',
			version: null,
			cluster: null,
			plan: null,
			apps: [],
			shareDetailsConsent: false,
			agreedToRegionConsent: false
		};
	},
	watch: {
		subdomain: {
			handler: debounce(function (value) {
				let invalidMessage = this.$validateSubdomain(value);
				this.$resources.subdomainExists.error = invalidMessage;
				if (!invalidMessage) {
					this.$resources.subdomainExists.submit();
				}
			}, 500)
		}
	},
	resources: {
		options() {
			return {
				url: 'press.api.client.run_doctype_method',
				params: {
					doctype: 'Site',
					method: 'options_for_new',
					selected_values: {
						version: this.version,
						apps: this.apps
					},
					lang: this.$i18n.locale
				},
				auto: true
			};
		},
		subdomainExists() {
			return {
				url: 'press.api.site.exists',
				params: {
					domain: this.options?.domain,
					subdomain: this.subdomain
				},
				validate() {
					return this.$validateSubdomain(this.subdomain);
				},
				transform(data) {
					return !Boolean(data);
				}
			};
		},
		newSite() {
			if (!this.options) return;
			let apps = ['frappe'].concat(this.apps);
			return {
				url: 'press.api.client.insert',
				params: {
					doc: {
						doctype: 'Site',
						subdomain: this.subdomain,
						apps: apps.map(app => ({ app })),
						cluster: this.cluster,
						bench: this.options.bench
					},
					lang: this.$i18n.locale
				},
				validate() {
					// let canCreate =
					// 	this.subdomainValid &&
					// 	this.selectedApps.length > 0 &&
					// 	this.selectedPlan &&
					// 	(!this.wantsToRestore || this.selectedFiles.database);

					if (!this.agreedToRegionConsent) {
						return this.$t('NewSite_content_3');
					}

					// if (!canCreate) {
					// 	return 'Cannot create site';
					// }
				},
				onSuccess: site => {
					router.push({
						name: 'Site Detail Jobs',
						params: { name: site.name }
					});
				}
			};
		}
	},
	computed: {
		options() {
			return this.$resources.options.data;
		}
	},
	methods: {
		toggleApp(app) {
			if (app.app == 'frappe') {
				return;
			}
			if (this.apps.includes(app.value)) {
				this.apps = this.apps.filter(a => a !== app.value);
			} else {
				this.apps.push(app.value);
			}
		}
	}
};
</script>
