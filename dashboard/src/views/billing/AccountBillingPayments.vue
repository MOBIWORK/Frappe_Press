<template>
	<Card
		:title="$t('invoices')"
		:subtitle="this.$t('AccountBillingPayments_1')"
		v-if="!invoiceName"
	>
		<div class="mb-4 grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
			<FormControl
				class="w-full"
				:label="$t('start_time')"
				v-model="filters.start_time"
				type="date"
			></FormControl>
			<FormControl
				class="w-full"
				:label="$t('end_time')"
				v-model="filters.end_time"
				type="date"
			></FormControl>
			<FormControl
				:label="$t('status')"
				type="select"
				:options="optionsStatus"
				v-model="filters.status"
			/>
			<div class="flex items-end">
				<Tooltip :text="$t('clear_filter')">
					<Button theme="gray" variant="subtle" @click="clearFilter">
						<ClearFilterIcon class="h-4 w-4" />
					</Button>
				</Tooltip>
			</div>
		</div>
		<div>
			<div class="max-h-96 overflow-auto">
				<table class="table w-full border-separate">
					<thead>
						<tr class="text-base text-gray-600">
							<th
								class="sticky top-0 min-w-28 border-b bg-white px-2 py-4 text-left"
							>
								{{ $t('invoice_code') }}
							</th>
							<th
								class="sticky top-0 min-w-28 border-b bg-white px-2 py-4 text-left"
							>
								{{ $t('invoice_date') }}
							</th>
							<th
								class="sticky top-0 min-w-28 border-b bg-white px-2 py-4 text-left"
							>
								{{ $t('description') }}
							</th>
							<th
								class="sticky top-0 min-w-28 border-b bg-white px-2 py-4 text-right"
							>
								{{ $t('amount_of_money') }} (VND)
							</th>
							<th
								class="sticky top-0 min-w-32 border-b bg-white px-2 py-4 text-left"
							>
								{{ $t('status') }}
							</th>
							<th
								class="sticky top-0 min-w-28 border-b bg-white px-2 py-4 text-left"
							>
								{{ $t('payment_date') }}
							</th>
							<th
								class="sticky top-0 min-w-28 border-b bg-white px-2 py-4 text-left"
							></th>
						</tr>
					</thead>
					<tbody class="text-center text-base text-gray-600" v-if="!invoices">
						<tr>
							<td class="px-2 py-4" colspan="7">
								<div class="flex justify-center">
									<LoadingText :text="$t('Loading') + '...'" />
								</div>
							</td>
						</tr>
					</tbody>
					<tbody v-else-if="invoices?.length">
						<tr
							v-for="invoice in invoices"
							:key="invoice.name"
							class="text-base text-gray-900"
						>
							<td class="border-b px-2 py-4">
								<Link
									v-if="['Subscription'].includes(invoice.type)"
									:to="'/billing/' + invoice.name + '/invoices'"
								>
									{{ invoice.name }}
								</Link>
							</td>
							<td class="border-b px-2 py-4">
								{{ this.$formatDate(invoice.due_date) }}
							</td>
							<td class="border-b px-2 py-4 text-gray-700">
								<span v-if="['Subscription'].includes(invoice.type)">
									{{ $t('invoice_for') }}
									{{ this.$formatDate(invoice.period_end, 'MM-yyyy') }}
								</span>
								<span v-else-if="invoice.type === 'Prepaid Credits'">
									{{ $t('Prepaid Credits') }}
								</span>
								<span v-else-if="invoice.type === 'Transferred Credits'">
									{{ $t('Transferred Credits') }}
								</span>
							</td>
							<td class="border-b px-2 py-4 text-right">
								{{ invoice.formatted_total }}
							</td>
							<td class="whitespace-nowrap border-b px-2 py-4">
								<Badge :label="this.$invoiceStatus(invoice.status)" />
							</td>
							<td class="border-b px-2 py-4">
								<span v-if="invoice.payment_date">
									{{ this.$formatDate(invoice.payment_date) }}
								</span>
							</td>
							<td class="border-b px-2 py-4">
								<div class="flex items-center justify-end space-x-2">
									<Button
										v-if="invoice.link_to_electronic_invoice"
										icon-left="download"
										class="shrink-0"
										:link="invoice.link_to_electronic_invoice"
									>
										<span class="text-sm">{{ $t('download') }}</span>
									</Button>
									<Button
										v-if="
											invoice.status != 'Paid' && invoice.stripe_invoice_url
										"
										icon-left="external-link"
										class="shrink-0"
										@click="payNow(invoice)"
									>
										<span class="text-sm">{{ $t('pay_now') }}</span>
									</Button>
								</div>
							</td>
						</tr>
					</tbody>
					<tbody class="text-center text-base text-gray-600" v-else>
						<tr>
							<td class="px-2 py-4" colspan="7">
								{{ $t('no_results') }}
							</td>
						</tr>
					</tbody>
				</table>
			</div>
			<div class="flex flex-wrap items-center justify-end py-2">
				<Pagination
					v-if="invoices?.length"
					:options="optionsPagination"
					@updatePage="updatePage"
				/>
			</div>
		</div>
	</Card>
	<InvoiceUsageCard :invoice="invoiceName" v-else />
</template>
<script>
import InvoiceUsageCard from '@/components/InvoiceUsageCard.vue';
import Pagination from '@/components/Table/Pagination.vue';
import ClearFilterIcon from '@/components/icons/ClearFilterIcon.vue';
import { watchDebounced } from '@vueuse/core';

export default {
	name: 'AccountBillingPayments',
	props: ['invoiceName'],
	components: {
		InvoiceUsageCard,
		Pagination,
		ClearFilterIcon
	},
	data() {
		return {
			invoiceStatus: '',
			invoices: null,
			optionsStatus: [
				{
					label: this.$t('all_invoices'),
					value: ''
				},
				{
					label: this.$t('unpaid_invoices'),
					value: 'Unpaid'
				},
				{
					label: this.$t('paid_invoices'),
					value: 'Paid'
				}
			],
			filters: this.setDefaultFilter(),
			optionsPagination: {
				currentPage: 1,
				totalPages: 0,
				pageSize: 20,
				total: 0
			}
		};
	},
	created() {
		if (this.$route.query.invoiceStatus)
			this.invoiceStatus = this.$route.query.invoiceStatus;
	},
	resources: {
		pastInvoices() {
			return {
				url: 'press.api.billing.invoices_and_payments',
				onSuccess(data) {
					this.optionsPagination = {
						currentPage: data?.pagination?.page,
						totalPages: data?.pagination.total_page,
						pageSize: data?.pagination.page_length,
						total: data?.pagination.total
					};
					this.invoices = data?.result;
				}
			};
		}
	},
	mounted() {
		watchDebounced(
			() => ({ ...this.filters }),
			val => {
				this.invoices = null;
				this.getInvoices();
			},
			{ debounce: 300, maxWait: 1000, deep: true, immediate: true }
		);
	},
	methods: {
		setDefaultFilter() {
			return {
				start_time: this.$startTimeOfMonth(1),
				end_time: this.$endTimeOfMonth(),
				status: '',
				page: 1
			};
		},
		clearFilter() {
			this.filters = this.setDefaultFilter();
		},
		getInvoices() {
			this.$resources.pastInvoices.submit(this.filters);
		},
		async refreshLink(invoiceName) {
			let refreshed_link = await this.$call(
				'press.api.billing.refresh_invoice_link',
				{
					invoice: invoiceName
				}
			);
			if (refreshed_link) {
				window.open(refreshed_link, '_blank');
			}
		},
		payNow(invoice) {
			if (invoice.stripe_link_expired) {
				this.refreshLink(invoice.name);
			} else {
				window.open(invoice.stripe_invoice_url, '_blank');
			}
		}
	}
};
</script>
