<template>
	<div>
		<header
			class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5"
		>
			<Breadcrumbs
				:items="[{ label: 'Benches', route: { name: 'BenchesScreen' } }]"
			>
				<template v-slot:actions>
					<Button
						variant="solid"
						icon-left="plus"
						:label="$t('Create')"
						class="ml-2"
						@click="showBillingDialog"
					/>
				</template>
			</Breadcrumbs>
		</header>

		<div class="mx-5 mt-5">
			<div class="flex">
				<div class="flex w-full space-x-2 pb-4">
					<FormControl :label="$t('Search_Benches')" v-model="searchTerm">
						<template #prefix>
							<FeatherIcon name="search" class="w-4 text-gray-600" />
						</template>
					</FormControl>
					<FormControl
						:label="$t('Status')"
						class="mr-8"
						type="select"
						:options="benchStatusFilterOptions"
						v-model="bench_status"
					/>
					<FormControl
						v-if="$resources.benchTags.data.length > 0"
						:label="$t('Tag')"
						class="mr-8"
						type="select"
						:options="benchTagFilterOptions"
						v-model="bench_tag"
					/>
				</div>
				<div class="w-10"></div>
			</div>
			<Table
				:columns="getHeaderTable()"
				:rows="benches"
				v-slot="{ rows, columns }"
			>
				<TableHeaderCustom :columns="getHeaderTable()" class="hidden lg:grid" />
				<TableRow
					v-for="row in rows"
					:key="row.name"
					:row="row"
					class="rounded"
				>
					<TableCell v-for="column in columns">
						<Badge
							v-if="column.name === 'status'"
							:label="this.$jobStatus(row.status)"
						/>
						<div
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
						</div>
						<div
							v-else-if="column.name === 'stats'"
							class="hidden text-sm text-gray-600 md:block"
						>
							{{
								`${row.stats.number_of_sites} ${$plural(
									row.stats.number_of_sites,
									$t('Site'),
									$t('Sites')
								)}`
							}}
							&middot;
							{{
								`${row.stats.number_of_apps} ${$plural(
									row.stats.number_of_apps,
									$t('App'),
									$t('Apps')
								)}`
							}}
						</div>
						<div v-else-if="column.name == 'actions'" class="w-full text-right">
							<Dropdown @click.prevent :options="dropdownItems(row)">
								<template v-slot="{ open }">
									<Button
										:variant="open ? 'subtle' : 'ghost'"
										class="mr-2"
										icon="more-horizontal"
									/>
								</template>
							</Dropdown>
						</div>
						<span
							v-else
							:class="{ 'hidden md:block': column.name === 'version' }"
							>{{ row[column.name] || '' }}
						</span>
					</TableCell>
				</TableRow>
				<div class="mt-8 flex items-center justify-center">
					<LoadingText
						v-if="$resources.allBenches.loading && !$resources.allBenches.data"
					/>
					<div
						v-else-if="$resources.allBenches.fetched && rows.length === 0"
						class="text-base text-gray-700"
					>
						{{ $t('No_Benches') }}
					</div>
				</div>
			</Table>
		</div>

		<Dialog
			:options="{ title: $t('Benches_content_1') }"
			v-model="showAddCardDialog"
		>
			<template v-slot:body-content>
				<StripeCard
					class="mb-1"
					v-if="showAddCardDialog"
					@complete="
						showAddCardDialog = false;
						$resources.paymentMethods.reload();
					"
				/>
			</template>
		</Dialog>
	</div>
</template>

<script>
import Table from '@/components/Table/Table.vue';
import TableCell from '@/components/Table/TableCell.vue';
import TableHeaderCustom from '@/components/Table/TableHeaderCustom.vue';
import TableRow from '@/components/Table/TableRow.vue';
import { defineAsyncComponent } from 'vue';

export default {
	name: 'BenchesScreen',
	data() {
		return {
			showAddCardDialog: false,
			searchTerm: '',
			bench_status: 'All',
			bench_tag: ''
		};
	},
	pageMeta() {
		return {
			title: 'Benches - MBWCloud'
		};
	},
	components: {
		Table,
		TableRow,
		TableCell,
		TableHeaderCustom,
		StripeCard: defineAsyncComponent(() =>
			import('@/components/StripeCard.vue')
		)
	},
	resources: {
		paymentMethods: {
			url: 'press.api.billing.get_payment_methods',
			auto: true
		},
		allBenches() {
			return {
				url: 'press.api.bench.all',
				params: {
					bench_filter: { status: this.bench_status, tag: this.bench_tag }
				},
				auto: true,
				cache: [
					'BenchList',
					this.bench_status,
					this.bench_tag,
					this.$account.team.name
				]
			};
		},
		benchTags: {
			url: 'press.api.bench.bench_tags',
			auto: true,
			initialData: []
		}
	},
	computed: {
		benches() {
			if (!this.$resources.allBenches.data) {
				return [];
			}
			let benches = this.$resources.allBenches.data.filter(bench =>
				this.$account.hasPermission(bench.name, '', true)
			);
			if (this.searchTerm)
				benches = benches.filter(bench =>
					bench.title.toLowerCase().includes(this.searchTerm.toLowerCase())
				);

			return benches.map(bench => ({
				name: bench.title,
				status: bench.status,
				version: bench.version,
				stats: {
					number_of_sites: bench.number_of_sites,
					number_of_apps: bench.number_of_apps
				},
				tags: bench.tags,
				route: { name: 'BenchSiteList', params: { benchName: bench.name } }
			}));
		},
		benchStatusFilterOptions() {
			return [
				{
					label: this.$t('All'),
					value: 'All'
				},
				{
					label: this.$t('Active'),
					value: 'Active'
				},
				{
					label: this.$t('Awaiting_Deploy'),
					value: 'Awaiting Deploy'
				}
			];
		},
		benchTagFilterOptions() {
			const defaultOptions = [
				{
					label: '',
					value: ''
				}
			];

			if (!this.$resources.benchTags.data) return defaultOptions;

			return [
				...defaultOptions,
				...this.$resources.benchTags.data.map(tag => ({
					label: tag,
					value: tag
				}))
			];
		}
	},
	methods: {
		getHeaderTable() {
			return [
				{ label: this.$t('Bench_Name'), name: 'name', width: 2 },
				{ label: this.$t('Status'), name: 'status', width: 1 },
				{ label: this.$t('Version'), name: 'version', width: 1 },
				{ label: this.$t('Tag'), name: 'tags', width: 1 },
				{ label: this.$t('Stats'), name: 'stats', width: 1 },
				{ label: '', name: 'actions', width: 0.5 }
			];
		},
		showBillingDialog() {
			// if (!this.$account.hasBillingInfo) {
			// 	this.showAddCardDialog = true;
			// } else {
			// 	this.$router.replace('/benches/new');
			// }

			this.$router.replace('/benches/new');
		},
		dropdownItems(bench) {
			return [
				{
					label: this.$t('New_Site'),
					onClick: () => {
						this.$router.push({
							name: 'NewBenchSite',
							params: { bench: bench.route.params.benchName }
						});
					},
					condition: () => bench.status === 'Active'
				},
				{
					label: this.$t('View_Sites'),
					onClick: () => {
						this.$router.push({
							name: 'BenchSiteList',
							params: { benchName: bench.route.params.benchName }
						});
					}
				}
			].filter(item => (item.condition ? item.condition() : true));
		}
	}
};
</script>
