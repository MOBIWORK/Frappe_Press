<template>
	<div>
		<div>
			<header
				class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5"
			>
				<Breadcrumbs
					:items="[{ label: $t('sites'), route: { name: 'Sites' } }]"
				>
					<template v-if="this.$account.team.enabled" #actions>
						<Button
							variant="solid"
							icon-left="plus"
							class="ml-2"
							:label="$t('create')"
							@click="showBillingDialog"
						>
						</Button>
					</template>
				</Breadcrumbs>
			</header>

			<div class="my-5 space-y-2 px-5">
				<div v-if="!$account.team.enabled">
					<Alert :title="$t('site_content_1')">
						{{ $t('site_content_2') }}
						<template #actions>
							<Button variant="solid" route="/settings/profile">
								{{ $t('enable_account') }}
							</Button>
						</template>
					</Alert>
				</div>
				<!-- <AlertBillingInformation /> -->
				<template v-if="showUnpaidInvoiceAlert">
					<Alert
						v-if="latestUnpaidInvoice.payment_mode === 'Prepaid Credits'"
						:title="$t('site_content_3')"
					>
						{{ $t('site_content_4') }}
						<strong>
							{{ this.$formatMoney(latestUnpaidInvoice.amount_due) }}
							{{ latestUnpaidInvoice.currency }}
						</strong>
						{{ $t('site_content_5') }}
						<template #actions>
							<Button @click="showPrepaidCreditsDialog = true" variant="solid">
								{{ $t('add_balance') }}
							</Button>
						</template>
					</Alert>

					<Alert v-else :title="$t('site_content_3')">
						{{ $t('site_content_6') }}
						<template v-if="this.$resources.latestUnpaidInvoice.data" #actions>
							<router-link
								:to="{ path: '/billing', query: { invoiceStatus: 'Unpaid' } }"
							>
								<Button variant="solid"> {{ $t('go_to_billing') }} </Button>
							</router-link>
						</template>
					</Alert>

					<PrepaidCreditsDialog
						v-if="showPrepaidCreditsDialog"
						v-model:show="showPrepaidCreditsDialog"
						:minimum-amount="Math.ceil(latestUnpaidInvoice.amount_due)"
						@success="handleAddPrepaidCreditsSuccess"
					/>
				</template>
			</div>
			<div class="mx-5">
				<div class="pb-20">
					<div class="flex">
						<div class="flex w-full space-x-2 pb-4">
							<FormControl :label="$t('search_sites')" v-model="searchTerm">
								<template #prefix>
									<FeatherIcon name="search" class="w-4 text-gray-600" />
								</template>
							</FormControl>
							<FormControl
								:label="$t('status')"
								class="mr-8"
								type="select"
								:options="siteStatusFilterOptions"
								v-model="site_status"
							/>
							<div class="flex items-end">
								<Tooltip :text="$t('Refresh')">
									<Button theme="gray" variant="subtle" @click="onReloadSites">
										<FeatherIcon name="refresh-cw" class="w-4 text-gray-700" />
									</Button>
								</Tooltip>
							</div>
							<!-- <FormControl
								v-if="$resources.siteTags.data.length > 0"
								label="Thẻ"
								class="mr-8"
								type="select"
								:options="siteTagFilterOptions"
								v-model="site_tag"
							/> -->
						</div>
					</div>
					<Table
						:columns="getHeaderTable()"
						:rows="sites"
						v-slot="{ rows, columns }"
					>
						<TableHeaderCustom
							:columns="getHeaderTable()"
							class="mb-4 hidden lg:grid"
						/>
						<div
							v-for="group in groups"
							:key="group.group"
							class="mb-4 rounded border"
						>
							<div
								class="flex w-full items-center rounded-t bg-gray-50 px-3 py-2 text-base"
							>
								<span class="font-semibold text-gray-900">
									{{ group.title }}
								</span>
								<span v-if="!group.public" class="ml-2 text-gray-600">{{
									group.version
								}}</span>
								<!-- <Button
									v-if="!group.public"
									variant="ghost"
									class="ml-auto"
									:route="{ name: 'Bench', params: { benchName: group.group } }"
								>
									Xem Bench
								</Button> -->
								<div v-else class="h-7" />
							</div>

							<TableRow
								v-for="(row, index) in sitesByGroup[group.group]"
								:key="row.name"
								:row="row"
								:class="index === 0 ? 'rounded-b' : 'rounded'"
							>
								<TableCell v-for="column in columns">
									<Badge
										v-if="column.name === 'status'"
										:label="$siteStatus(row)"
									/>
									<!-- <div
										v-else-if="column.name === 'tags'"
										class="hidden space-x-1 lg:flex"
									>
										<Badge
											v-for="(tag, i) in row.tags.slice(0, 1)"
											theme="blue"
											:label="tag"
										/>
										<Tooltip
											v-if="row.tags.length > 1"
											:text="row.tags.slice(1).join(', ')"
										>
											<Badge
												v-if="row.tags.length > 1"
												:label="`+${row.tags.length - 1}`"
											/>
										</Tooltip>
										<span v-if="row.tags.length == 0">-</span>
									</div> -->
									<span
										v-else-if="column.name === 'plan'"
										class="hidden md:block"
									>
										{{
											row.plan
												? `${$planTitle(row.plan)}${
														row.plan.price_vnd > 0 ? `/${$t('month')}` : ''
												  }`
												: ''
										}}
									</span>
									<div
										v-else-if="column.name === 'region'"
										class="hidden md:block"
									>
										<img
											v-if="row.server_region_info.image"
											class="h-4"
											:src="row.server_region_info.image"
											:alt="`Flag of ${row.server_region_info.title}`"
											:title="row.server_region_info.title"
										/>
										<span class="text-base text-gray-700" v-else>
											{{ row.server_region_info.title }}
										</span>
									</div>
									<div
										class="w-full text-right"
										v-else-if="column.name == 'actions'"
									>
										<Dropdown
											v-if="['Active', 'Updating'].includes(row.status)"
											@click.prevent
											:options="dropdownItems(row)"
										>
											<template v-slot="{ open }">
												<Button
													:variant="open ? 'subtle' : 'ghost'"
													icon="more-horizontal"
												/>
											</template>
										</Dropdown>
									</div>
									<span v-else>{{ row[column.name] || '' }}</span>
								</TableCell>
							</TableRow>
						</div>
						<div class="mt-8 flex items-center justify-center">
							<LoadingText
								v-if="$resources.allSites.loading && !$resources.allSites.data"
								:text="$t('Loading') + '...'"
							/>
							<div
								v-else-if="$resources.allSites.fetched && rows.length === 0"
								class="text-base text-gray-700"
							>
								{{ $t('no_sites') }}
							</div>
						</div>
					</Table>

					<Dialog
						:options="{
							title: $t('login_as_administrator'),
							actions: [
								{
									label: $t('proceed'),
									variant: 'solid',
									onClick: proceedWithLoginAsAdmin
								}
							]
						}"
						v-model="showReasonForAdminLoginDialog"
					>
						<template #body-content>
							<FormControl
								:label="$t('reason_for_logging_in_as_administrator')"
								type="textarea"
								v-model="reasonForAdminLogin"
								required
							/>
							<ErrorMessage class="mt-3" :message="errorMessage" />
						</template>
					</Dialog>
				</div>
			</div>
		</div>
	</div>
</template>
<script>
import { defineAsyncComponent } from 'vue';
import Table from '@/components/Table/Table.vue';
import TableHeaderCustom from '@/components/Table/TableHeaderCustom.vue';
import TableRow from '@/components/Table/TableRow.vue';
import TableCell from '@/components/Table/TableCell.vue';
import { loginAsAdmin } from '@/controllers/loginAsAdmin';
import AlertBillingInformation from '@/components/AlertBillingInformation.vue';
import { notify } from '@/utils/toast';
import { debounce } from 'lodash';

export default {
	name: 'Sites',
	pageMeta() {
		return {
			title: `${this.$t('sites')} - MBWCloud`
		};
	},
	props: ['bench'],
	components: {
		Table,
		TableHeaderCustom,
		TableRow,
		TableCell,
		PrepaidCreditsDialog: defineAsyncComponent(() =>
			import('@/components/PrepaidCreditsDialog.vue')
		),
		StripeCard: defineAsyncComponent(() =>
			import('@/components/StripeCard.vue')
		),
		AlertBillingInformation
	},
	data() {
		return {
			showPrepaidCreditsDialog: false,
			showAddCardDialog: false,
			searchTerm: '',
			reasonForAdminLogin: '',
			errorMessage: null,
			showReasonForAdminLoginDialog: false,
			siteForLogin: null,
			site_status: 'All',
			site_tag: ''
		};
	},
	resources: {
		allSites() {
			return {
				url: 'press.api.site.all',
				params: {
					site_filter: { status: this.site_status, tag: this.site_tag }
				},
				auto: true,
				cache: [
					'SiteList',
					this.site_status,
					this.site_tag,
					this.$account.team.name
				]
			};
		},
		siteTags: { url: 'press.api.site.site_tags', auto: true, initialData: [] },
		latestUnpaidInvoice: {
			url: 'press.api.billing.get_latest_unpaid_invoice',
			auto: true
		},
		loginAsAdmin() {
			return loginAsAdmin('placeholderSite'); // So that RM does not yell at first load
		}
	},
	mounted() {
		this.$socket.on('agent_job_update', this.onAgentJobUpdate);
		this.$socket.on('list_update', this.onSiteUpdate);
	},
	unmounted() {
		this.$socket.off('agent_job_update', this.onAgentJobUpdate);
		this.$socket.off('list_update', this.onSiteUpdate);
	},
	methods: {
		onReloadSites: debounce(function (e) {
			this.$resources.allSites.reload();
		}, 300),
		getHeaderTable() {
			return [
				{ label: this.$t('site_name'), name: 'name', width: 2 },
				{ label: this.$t('status'), name: 'status', width: 1 },
				{ label: this.$t('region'), name: 'region', width: 0.5 },
				// { label: 'Thẻ', name: 'tags', width: 1 },
				{ label: this.$t('plan'), name: 'plan', width: 1.5 },
				{ label: '', name: 'actions', width: 0.5 }
			];
		},
		showBillingDialog() {
			// if (!this.$account.hasBillingInfo) {
			// 	this.showAddCardDialog = true;
			// } else {
			// 	this.$router.replace('/sites/new');
			// }
			this.$router.replace('/sites/new');
		},
		onAgentJobUpdate(data) {
			if (!(data.name === 'New Site' || data.name === 'New Site from Backup'))
				return;
			if (data.status === 'Success' && data.user === this.$account.user.name) {
				this.reload();
				notify({
					title: this.$t('site_creation_complete'),
					message: this.$t('site_content_7'),
					icon: 'check',
					color: 'green'
				});
			}
		},
		onSiteUpdate(event) {
			// Refresh if the event affects any of the sites in the list view
			// TODO: Listen to a more granular event than list_update
			if (event.doctype === 'Site') {
				let sites = this.sites;
				if (
					event.user === this.$account.user.name ||
					sites.includes(event.name)
				) {
					this.reload();
				}
			}
		},
		reload() {
			// refresh if currently not loading and have not reloaded in the last 5 seconds
			if (
				!this.$resources.allSites.loading &&
				new Date() - this.$resources.allSites.lastLoaded > 5000
			) {
				this.$resources.allSites.reload();
			}
		},
		handleAddPrepaidCreditsSuccess() {
			this.$resources.latestUnpaidInvoice.reload();
			this.showPrepaidCreditsDialog = false;
		},
		dropdownItems(site) {
			return [
				{
					label: this.$t('visit_site'),
					onClick: () => {
						window.open(`https://${site.name}`, '_blank');
					}
				},
				{
					label: this.$t('login_as_administrator'),
					onClick: () => {
						if (this.$account.team.name === site.team) {
							return this.$resources.loginAsAdmin.submit({
								name: site.name
							});
						}

						this.siteForLogin = site.name;
						this.showReasonForAdminLoginDialog = true;
					}
				}
			];
		},
		proceedWithLoginAsAdmin() {
			this.errorMessage = '';

			if (!this.reasonForAdminLogin.trim()) {
				this.errorMessage = this.$t('reason_is_required');
				return;
			}

			this.$resources.loginAsAdmin.submit({
				name: this.siteForLogin,
				reason: this.reasonForAdminLogin
			});

			this.showReasonForAdminLoginDialog = false;
		}
	},
	computed: {
		sites() {
			if (!this.$resources.allSites.data) {
				return [];
			}
			let sites = this.$resources.allSites.data.filter(site =>
				this.$account.hasPermission(site.name, '', true)
			);
			if (this.searchTerm) {
				return sites.filter(site =>
					site.name.toLowerCase().includes(this.searchTerm.toLowerCase())
				);
			}
			return sites;
		},
		sitesByGroup() {
			let sitesByGroup = {};

			for (let site of this.sites) {
				let group = site.group;
				if (!sitesByGroup[group]) {
					sitesByGroup[group] = [];
				}
				site.route = {
					name: 'SiteOverview',
					params: {
						siteName: site.name
					}
				};
				sitesByGroup[group].push(site);
			}

			return sitesByGroup;
		},
		groups() {
			let seen = [];
			let groups = [];
			for (let site of this.sites) {
				if (site.public) {
					site.title = '';
					site.group = 'Shared';
				}
				if (!seen.includes(site.group)) {
					seen.push(site.group);
					if (site.public)
						groups.unshift({
							title: site.title,
							group: site.group,
							public: site.public,
							version: site.version
						});
					else
						groups.push({
							title: site.title,
							group: site.group,
							public: site.public,
							version: site.version
						});
				}
			}
			return groups;
		},
		showUnpaidInvoiceAlert() {
			if (!this.latestUnpaidInvoice) {
				return;
			}
			return !(
				this.$account.team.erpnext_partner || this.$account.team.free_account
			);
		},
		latestUnpaidInvoice() {
			if (this.$resources.latestUnpaidInvoice.data) {
				return this.$resources.latestUnpaidInvoice.data;
			}
		},
		siteStatusFilterOptions() {
			return [
				{
					label: this.$t('all'),
					value: 'All'
				},
				{
					label: this.$t('active'),
					value: 'Active'
				},
				{
					label: this.$t('broken'),
					value: 'Broken'
				},
				{
					label: this.$t('inactive'),
					value: 'Inactive'
				},
				{
					label: this.$t('trial'),
					value: 'Trial'
				},
				{
					label: this.$t('update_available'),
					value: 'Update Available'
				}
			];
		},
		siteTagFilterOptions() {
			const defaultOptions = [
				{
					label: '',
					value: ''
				}
			];

			if (!this.$resources.siteTags.data) return defaultOptions;

			return [
				...defaultOptions,
				...this.$resources.siteTags.data.map(tag => ({
					label: tag,
					value: tag
				}))
			];
		}
	}
};
</script>
