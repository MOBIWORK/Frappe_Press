<template>
	<Card
		:title="$t('Domains')"
		:subtitle="
			domains.data && domains.data.length
				? $t('Domains_pointing_to_your_site')
				: $t('No_domains_pointing_to_your_site')
		"
	>
		<template #actions>
			<Button
				@click="showDialog = true"
				:disabled="site.status === 'Suspended'"
			>
				{{ $t('Add_Domain') }}
			</Button>
		</template>
		<div class="divide-y" v-if="domains.data">
			<div v-for="d in domains.data" :key="d.name">
				<div class="py-2">
					<div class="flex items-center">
						<div class="flex w-2/3 text-base font-medium">
							<a
								class="text-blue-500"
								:href="'https://' + d.domain"
								target="_blank"
								v-if="d.status === 'Active'"
							>
								{{ d.domain }}
							</a>
							<span v-else>{{ d.domain }}</span>
							<div
								class="flex"
								v-if="d.redirect_to_primary == 1 && d.status == 'Active'"
							>
								<FeatherIcon name="arrow-right" class="mx-1 w-4" />
								<a
									class="text-blue-500"
									:href="'https://' + d.domain"
									target="_blank"
									v-if="d.status === 'Active'"
								>
									{{ site.host_name }}
								</a>
							</div>
						</div>
						<div class="ml-auto flex items-center space-x-2">
							<Badge
								v-if="d.status == 'Active' && d.primary"
								:label="'Primary'"
							/>
							<Badge v-else-if="d.status != 'Active'" :label="d.status" />
							<Button
								v-if="d.status == 'Broken' && d.retry_count <= 5"
								:loading="$resources.retryAddDomain.loading"
								@click="
									$resources.retryAddDomain.submit({
										name: site.name,
										domain: d.domain
									})
								"
							>
								{{ $t('Retry') }}
							</Button>
							<Button v-if="$resources.removeDomain.loading" :loading="true">
								{{ $t('Removing_domain') }}
							</Button>
							<Dropdown v-else :options="actionItems(d)">
								<template v-slot="{ open }">
									<Button icon="more-horizontal" />
								</template>
							</Dropdown>
						</div>
					</div>
					<ErrorMessage
						v-if="d.status == 'Broken'"
						:error="$t('SiteOverviewDomains_content_1')"
					/>
					<ErrorMessage :message="$resources.removeDomain.error" />
					<ErrorMessage :message="$resources.setHostName.error" />
				</div>
			</div>
		</div>
		<Dialog v-model="showDialog" :options="{ title: $t('Add_Domain') }">
			<template v-slot:body-content>
				<div class="space-y-4">
					<p class="text-base">
						{{ $t('SiteOverviewDomains_content_2') }}
					</p>
					<FormControl
						placeholder="www.example.com"
						v-model="newDomain"
						:readonly="dnsVerified"
					/>

					<div v-if="newDomain && !dnsVerified" class="space-y-2 text-base">
						<p>{{ $t('SiteOverviewDomains_content_3') }}</p>
						<p class="px-2">
							<span class="font-semibold text-gray-700">CNAME</span>
							{{ $t('record_from') }}
							<span class="font-semibold text-gray-700">{{ newDomain }}</span>
							{{ $t('to') }}
							<span class="font-semibold text-gray-700">{{ site.name }}</span>
						</p>
						<p class="px-2">
							<span class="font-semibold text-gray-700">A</span>
							{{ $t('record_from') }}
							<span class="font-semibold text-gray-700">{{ newDomain }}</span>
							{{ $t('to') }}
							<span class="font-semibold text-gray-700">{{ site.ip }}</span>
						</p>
					</div>
					<div v-if="dnsResult && !dnsResult.matched" class="space-y-2">
						<p class="text-base">
							{{ $t('SiteOverviewDomains_content_4') }}
							<span class="font-semibold text-gray-700">{{ newDomain }}</span
							>.
						</p>
						<div
							v-if="newDomain && dnsResult.CNAME && !dnsResult.CNAME.matched"
							class="space-y-2"
						>
							<p class="text-base">
								<span class="font-semibold text-gray-700">CNAME</span>
							</p>
							<div
								class="flex flex-row items-center justify-between rounded-lg border-2 p-2"
							>
								<p
									class="select-all overflow-hidden font-mono text-sm text-gray-800"
								>
									{{ dnsResult.CNAME.answer }}
								</p>
							</div>
						</div>
						<div
							v-if="newDomain && dnsResult.A && !dnsResult.A.matched"
							class="space-y-2"
						>
							<p class="text-base">
								<span class="font-semibold text-gray-700">A</span>
							</p>
							<div
								class="flex flex-row items-center justify-between rounded-lg border-2 p-2"
							>
								<p
									class="select-all overflow-hidden font-mono text-sm text-gray-800"
								>
									{{ dnsResult.A.answer }}
								</p>
							</div>
						</div>
					</div>
					<p class="flex text-base" v-if="dnsVerified === false">
						<FeatherIcon
							name="x"
							class="mr-2 h-5 w-5 rounded-full bg-red-100 p-1 text-red-500"
						/>
						{{ $t('DNS_Verification_Failed') }}
					</p>
					<p class="flex text-base" v-if="dnsVerified === true">
						<FeatherIcon
							name="check"
							class="mr-2 h-5 w-5 rounded-full bg-green-100 p-1 text-green-500"
						/>
						{{ $t('SiteOverviewDomains_content_5') }}
					</p>
					<ErrorMessage :message="$resources.checkDNS.error" />
					<ErrorMessage :message="$resources.addDomain.error" />
					<ErrorMessage :message="$resources.retryAddDomain.error" />
				</div>
			</template>

			<template #actions>
				<Button
					v-if="!dnsVerified"
					class="mt-2 w-full"
					variant="solid"
					:loading="$resources.checkDNS.loading"
					@click="
						$resources.checkDNS.submit({
							name: site.name,
							domain: newDomain
						})
					"
				>
					{{ $t('Verify') }}
				</Button>
				<Button
					v-if="dnsVerified"
					class="mt-2 w-full"
					variant="solid"
					:loading="$resources.addDomain.loading"
					@click="
						$resources.addDomain.submit({
							name: site.name,
							domain: newDomain
						})
					"
				>
					{{ $t('Add_Domain') }}
				</Button>
			</template>
		</Dialog>
	</Card>
</template>

<script>
import { notify } from '@/utils/toast';

export default {
	name: 'SiteOverviewDomains',
	props: ['site'],
	data() {
		return {
			showDialog: false,
			newDomain: null
		};
	},
	resources: {
		domains() {
			return {
				url: 'press.api.site.domains',
				params: { name: this.site?.name },
				auto: true
			};
		},
		checkDNS: {
			url: 'press.api.site.check_dns',
			validate() {
				if (!this.newDomain) return this.$t('Domain_cannot_be_empty');
			}
		},
		addDomain: {
			url: 'press.api.site.add_domain',
			onSuccess() {
				this.$resources.checkDNS.reset();
				this.$resources.domains.reload();
				this.showDialog = false;
			}
		},
		removeDomain: {
			url: 'press.api.site.remove_domain',
			onSuccess() {
				this.$resources.domains.reload();
			}
		},
		retryAddDomain: {
			url: 'press.api.site.retry_add_domain',
			onSuccess() {
				this.$resources.domains.fetch();
			}
		},
		setHostName: {
			url: 'press.api.site.set_host_name',
			onSuccess() {
				this.$resources.domains.reload();
			}
		},
		setupRedirect: {
			url: 'press.api.site.set_redirect',
			onSuccess() {
				this.$resources.domains.reload();
			}
		},
		removeRedirect: {
			url: 'press.api.site.unset_redirect',
			onSuccess() {
				this.$resources.domains.reload();
			}
		}
	},
	computed: {
		domains() {
			return this.$resources.domains;
		},
		dnsVerified() {
			return this.dnsResult?.matched;
		},
		dnsResult() {
			return this.$resources.checkDNS.data;
		},
		primaryDomain() {
			return this.$resources.domains.data.filter(d => d.primary)[0].domain;
		}
	},
	watch: {
		newDomain() {
			this.$resources.checkDNS.reset();
		}
	},
	methods: {
		actionItems(domain) {
			return [
				{
					label: this.$t('remove'),
					onClick: () => this.confirmRemoveDomain(domain.domain)
				},
				{
					label: this.$t('Set_Primary'),
					condition: () => domain.status == 'Active' && !domain.primary,
					onClick: () => this.confirmSetPrimary(domain.domain)
				},
				{
					label: this.$t('Redirect_to_Primary'),
					condition: () =>
						domain.status == 'Active' &&
						!domain.primary &&
						!domain.redirect_to_primary,
					onClick: () => this.confirmSetupRedirect(domain.domain)
				},
				{
					label: this.$t('Remove_Redirect'),
					condition: () =>
						domain.status == 'Active' &&
						!domain.primary &&
						domain.redirect_to_primary,
					onClick: () => this.confirmRemoveRedirect(domain.domain)
				}
			].filter(d => (d.condition ? d.condition() : true));
		},
		confirmRemoveDomain(domain) {
			this.$confirm({
				title: this.$t('Remove_Domain'),
				message: `${this.$t(
					'SiteOverviewDomains_content_6'
				)} <b>${domain}</b>?`,
				actionLabel: this.$t('remove'),
				actionColor: 'red',
				action: closeDialog => {
					closeDialog();
					this.$resources.removeDomain.submit({
						name: this.site.name,
						domain: domain
					});
				}
			});
		},
		confirmSetPrimary(domain) {
			let workingRedirects = false;
			this.$resources.domains.data.forEach(d => {
				if (d.redirect_to_primary) {
					workingRedirects = true;
				}
			});

			if (workingRedirects) {
				notify({
					title: this.$t('SiteOverviewDomains_content_7'),
					color: 'red',
					icon: 'x'
				});
			} else {
				this.$confirm({
					title: this.$t('Set_as_Primary_Domain'),
					message: `${this.$t(
						'SiteOverviewDomains_content_8'
					)} <b>${domain}</b> ${this.$t('SiteOverviewDomains_content_9')}`,
					actionLabel: this.$t('Set_Primary'),
					action: closeDialog => {
						closeDialog();
						this.$resources.setHostName.submit({
							name: this.site.name,
							domain: domain
						});
					}
				});
			}
		},
		confirmSetupRedirect(domain) {
			this.$confirm({
				title: this.$t('Redirect_to_Primary_Domain'),
				message: `${this.$t(
					'SiteOverviewDomains_content_10'
				)} <b>${domain}</b> ${this.$t('to')} <b>${
					this.primaryDomain
				}</b>. ${this.$t('SiteOverviewDomains_content_11')}`,
				actionLabel: this.$t('Redirect_to_Primary'),
				action: closeDialog => {
					closeDialog();
					this.$resources.setupRedirect.submit({
						name: this.site.name,
						domain: domain
					});
				}
			});
		},
		confirmRemoveRedirect(domain) {
			this.$confirm({
				title: this.$t('Remove_Redirect'),
				message: `${this.$t(
					'SiteOverviewDomains_content_12'
				)} <b>${domain}</b> ${this.$t('to')} <b>${
					this.primaryDomain
				}</b>. ${this.$t('SiteOverviewDomains_content_11')}`,
				actionLabel: this.$t('Remove_Redirect'),
				action: closeDialog => {
					closeDialog();
					this.$resources.removeRedirect.submit({
						name: this.site.name,
						domain: domain
					});
				}
			});
		}
	}
};
</script>
