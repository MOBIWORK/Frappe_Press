<template>
	<div>
		<div v-if="server">
			<div>
				<header
					class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5"
				>
					<Breadcrumbs
						:items="[
							{ label: 'Servers', route: { name: 'Servers' } },
							{
								label: server?.title,
								route: {
									name: 'ServerOverview',
									params: { serverName: server?.name }
								}
							}
						]"
					>
						<template #actions>
							<div>
								<Button
									v-if="server?.status === 'Active'"
									icon-left="plus"
									label="New Bench"
									@click="
										$router.push({
											name: 'NewServerBench',
											params: { server: server?.name }
										})
									"
								/>
								<Dropdown :options="serverActions">
									<template v-slot="{ open }">
										<Button
											variant="ghost"
											class="mr-2"
											icon="more-horizontal"
										/>
									</template>
								</Dropdown>
							</div>
						</template>
					</Breadcrumbs>
				</header>

				<EditServerTitleDialog v-model="showEditTitleDialog" :server="server" />

				<div
					class="flex flex-col space-y-3 px-5 py-3 md:flex-row md:items-baseline md:justify-between md:space-y-0"
				>
					<div class="mt-2 flex items-center">
						<h1 class="text-2xl font-bold">{{ server.title }}</h1>
						<Badge class="ml-4" :label="server.status" />

						<div
							v-if="regionInfo"
							class="ml-2 hidden cursor-default flex-row items-center self-end rounded-md bg-yellow-50 px-3 py-1 text-xs font-medium text-yellow-700 md:flex"
						>
							<img
								v-if="regionInfo.image"
								class="mr-2 h-4"
								:src="regionInfo.image"
								:alt="`Flag of ${regionInfo.title}`"
								:title="regionInfo.image"
							/>
							<p>{{ regionInfo.title }}</p>
						</div>
					</div>
					<div class="mb-10 flex flex-row justify-between md:hidden">
						<div class="flex flex-row">
							<div
								v-if="regionInfo"
								class="flex cursor-default flex-row items-center rounded-md bg-yellow-50 px-3 py-1 text-xs font-medium text-yellow-700"
							>
								<img
									v-if="regionInfo.image"
									class="mr-2 h-4"
									:src="regionInfo.image"
									:alt="`Flag of ${regionInfo.title}`"
									:title="regionInfo.image"
								/>
								<p>{{ regionInfo.title }}</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
		<div class="p-5 pt-1">
			<Tabs :tabs="tabs">
				<router-view v-slot="{ Component, route }">
					<component v-if="server" :is="Component" :server="server"></component>
				</router-view>
			</Tabs>
		</div>
	</div>
</template>

<script>
import EditServerTitleDialog from './EditServerTitleDialog.vue';
import Tabs from '@/components/Tabs.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'Server',
	pageMeta() {
		return {
			title: `Server - ${this.serverName} - MBWCloud`
		};
	},
	props: ['serverName'],
	components: {
		EditServerTitleDialog,
		Tabs
	},
	data() {
		return {
			runningJob: false,
			runningPlay: false,
			showEditTitleDialog: false,
			errorMessage: ''
		};
	},
	resources: {
		server() {
			return {
				url: 'press.api.server.get',
				params: {
					name: this.serverName
				},
				auto: true,
				onSuccess() {
					this.routeToGeneral();
				},
				onError: this.$routeTo404PageIfNotFound
			};
		},
		reboot() {
			return {
				url: 'press.api.server.reboot',
				params: {
					name: this.serverName
				},
				onSuccess(data) {
					notify({
						title: 'Server Reboot Scheduled Successfully',
						color: 'green',
						icon: 'check'
					});
					this.$resources.server.reload();
				},
				onError() {
					notify({
						title: 'Có lỗi xảy ra',
						color: 'red',
						icon: 'x'
					});
				}
			};
		}
	},
	methods: {
		routeToGeneral() {
			if (this.$route.matched.length === 1) {
				let path = this.$route.fullPath;
				this.$router.replace(`${path}/overview`);
			}
		}
	},
	computed: {
		server() {
			return this.$resources.server.data;
		},

		regionInfo() {
			if (!this.$resources.server.loading && this.$resources.server.data) {
				return this.$resources.server.data.region_info;
			}
			return null;
		},

		serverActions() {
			return [
				{
					label: 'Chỉnh sửa tiêu đề',
					icon: 'edit',
					onClick: () => (this.showEditTitleDialog = true)
				},
				['Active', 'Updating'].includes(this.server.status) && {
					label: 'Visit Server',
					icon: 'external-link',
					onClick: () => {
						window.open(`https://${this.server.name}`, '_blank');
					}
				},
				this.$account.user.user_type == 'System User' && {
					label: 'View in Desk',
					icon: 'external-link',
					onClick: () => {
						window.open(
							`${window.location.protocol}//${window.location.host}/app/server/${this.server.name}`,
							'_blank'
						);
					}
				},
				this.server.status === 'Active' &&
					this.$account.hasPermission(
						this.server.name,
						'press.api.server.reboot'
					) && {
						label: 'Reboot',
						icon: 'tool',
						loading: this.$resources.reboot.loading,
						onClick: () => {
							return this.$resources.reboot.submit();
						}
					},
				this.$account.user.user_type == 'System User' && {
					label: 'Impersonate Team',
					icon: 'tool',
					onClick: async () => {
						await this.$account.switchTeam(this.server.team);
						notify({
							title: 'Switched Team',
							message: `Switched to ${this.server.team}`,
							icon: 'check',
							color: 'green'
						});
					}
				}
			].filter(Boolean);
		},

		tabs() {
			let tabRoute = subRoute => `/servers/${this.serverName}/${subRoute}`;
			let tabs = [
				{ label: 'Installing', route: 'install' },
				{ label: 'Overview', route: 'overview' },
				{ label: 'Analytics', route: 'analytics' },
				{ label: 'Benches', route: 'benches' },
				{ label: 'Jobs', route: 'jobs', showRedDot: this.runningJob },
				{ label: 'Plays', route: 'plays', showRedDot: this.runningPlay },
				{ label: 'Settings', route: 'settings' }
			];

			let tabsByStatus = {
				Active: [
					'Overview',
					'Analytics',
					'Benches',
					'Jobs',
					'Plays',
					'Settings'
				],
				Pending: ['Installing'],
				Installing: ['Installing', 'Plays']
			};
			if (this.server) {
				let tabsToShow = tabsByStatus[this.server.status];
				if (tabsToShow?.length) {
					tabs = tabs.filter(tab => tabsToShow.includes(tab.label));
				}
				return tabs.map(tab => {
					return {
						...tab,
						route: tabRoute(tab.route)
					};
				});
			}
			return [];
		}
	}
};
</script>
