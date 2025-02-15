<template>
	<div v-if="bench">
		<header
			class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5"
		>
			<Breadcrumbs
				:items="[
					{ label: 'Benches', route: { name: 'BenchesScreen' } },
					{
						label: bench?.title,
						route: {
							name: 'BenchSiteList',
							params: { benchName: bench?.name }
						}
					}
				]"
			>
				<template #actions>
					<div class="space-x-2">
						<Button
							v-if="bench?.status === 'Active'"
							icon-left="plus"
							:label="$t('New_Site')"
							@click="$router.push(`/${this.bench.name}/new`)"
						/>
						<Dropdown :options="benchActions">
							<template v-slot="{ open }">
								<Button variant="ghost" icon="more-horizontal" />
							</template>
						</Dropdown>
					</div>
				</template>
			</Breadcrumbs>
		</header>

		<EditBenchTitleDialog v-model="showEditTitleDialog" :bench="bench" />
		<BenchDropDialog v-model="showDropBenchDialog" :bench="bench" />

		<div class="p-5">
			<div
				class="flex flex-col space-y-3 md:flex-row md:items-baseline md:justify-between md:space-y-0"
			>
				<div class="flex items-center">
					<h1 class="text-2xl font-bold">{{ bench.title }}</h1>
					<Badge class="ml-4" :label="this.$jobStatus(bench.status)" />
				</div>
			</div>
			<div class="mb-2 mt-4">
				<AlertBenchUpdate v-if="bench?.no_sites <= 0" :bench="bench" />
				<AlertUpdate v-else :bench="bench" />
			</div>
			<Tabs :tabs="tabs">
				<router-view v-slot="{ Component }">
					<component v-if="bench" :is="Component" :bench="bench"></component>
				</router-view>
			</Tabs>
		</div>
	</div>
</template>

<script>
import BenchDropDialog from './BenchDropDialog.vue';
import Tabs from '@/components/Tabs.vue';
import AlertUpdate from '@/components/AlertUpdate.vue';
import AlertBenchUpdate from '@/components/AlertBenchUpdate.vue';
import EditBenchTitleDialog from './EditBenchTitleDialog.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'Bench',
	pageMeta() {
		return {
			title: `Bench - ${this.bench?.title || 'Private'} - EOV Cloud`
		};
	},
	props: ['benchName'],
	components: {
		Tabs,
		BenchDropDialog,
		AlertUpdate,
		AlertBenchUpdate,
		EditBenchTitleDialog
	},
	data() {
		return {
			showDropBenchDialog: false,
			showEditTitleDialog: false
		};
	},
	resources: {
		bench() {
			return {
				url: 'press.api.bench.get',
				params: {
					name: this.benchName
				},
				auto: true,
				onError: this.$routeTo404PageIfNotFound
			};
		},
		updateAllSites() {
			return {
				url: 'press.api.bench.update_all_sites',
				params: {
					name: this.benchName
				},
				onSuccess() {
					notify({
						title: this.$t('Switched_Team'),
						message: `${this.$t('Switched_to')} ${this.bench.team}`,
						icon: 'check',
						color: 'green'
					});
				},
				onError(e) {
					notify({
						title: e,
						icon: 'x',
						color: 'red'
					});
				}
			};
		}
	},
	activated() {
		this.$socket.on('list_update', this.onSocketUpdate);
	},
	deactivated() {
		this.$socket.off('list_update', this.onSocketUpdate);
	},
	methods: {
		onSocketUpdate({ doctype, name }) {
			if (doctype == 'Release Group' && name == this.bench.name) {
				this.reloadBench();
			}
		},
		reloadBench() {
			// reload if not loaded in last 1 second
			let seconds = 1;
			if (new Date() - this.$resources.bench.lastLoaded > 1000 * seconds) {
				this.$resources.bench.reload();
			}
		},
		isSaasLogin(app) {
			if (localStorage.getItem('saas_login')) {
				return `/saas/manage/${app}/benches`;
			}

			return '/sites';
		}
	},
	computed: {
		bench() {
			if (this.$resources.bench?.data && !this.$resources.bench.loading) {
				return this.$resources.bench.data;
			}
		},
		tabs() {
			let tabRoute = subRoute => `/benches/${this.benchName}/${subRoute}`;
			let tabs = [
				{
					label: this.$t('Sites'),
					route: 'sites'
				},
				{ label: this.$t('Apps'), route: 'apps' },
				{ label: this.$t('Deploys'), route: 'deploys' },
				{
					label: this.$t('Config'),
					route: 'bench-config',
					condition: () => !this.bench?.public
				},
				{ label: this.$t('Jobs'), route: 'jobs' },
				{ label: this.$t('Settings'), route: 'settings' }
			].filter(tab => (tab.condition ? tab.condition() : true));

			if (this.bench) {
				return tabs.map(tab => {
					return {
						...tab,
						route: tabRoute(tab.route)
					};
				});
			}
			return [];
		},
		benchActions() {
			return [
				{
					label: this.$t('Edit_Title'),
					icon: 'edit',
					onClick: () => (this.showEditTitleDialog = true)
				},
				{
					label: this.$t('view_in_desk'),
					icon: 'external-link',
					condition: () => this.$account.user.user_type == 'System User',
					onClick: () => {
						window.open(
							`${window.location.protocol}//${window.location.host}/app/release-group/${this.bench.name}`,
							'_blank'
						);
					}
				},
				{
					label: this.$t('Impersonate_Team'),
					icon: 'tool',
					condition: () => this.$account.user.user_type == 'System User',
					onClick: async () => {
						await this.$account.switchTeam(this.bench.team);
					}
				},
				{
					label: this.$t('Update_All_Sites'),
					icon: 'arrow-up-circle',
					condition: () => this.bench.status == 'Active' && !this.bench.public,
					onClick: async () => {
						await this.$resources.updateAllSites.submit();
						notify({
							title: this.$t('AlertSiteUpdate_content_5'),
							message: this.$t('Bench_content_1'),
							icon: 'check',
							color: 'green'
						});
					}
				},
				{
					label: this.$t('Drop_Bench'),
					icon: 'trash',
					condition: () => !this.bench.public,
					onClick: () => (this.showDropBenchDialog = true)
				}
			];
		}
	}
};
</script>
