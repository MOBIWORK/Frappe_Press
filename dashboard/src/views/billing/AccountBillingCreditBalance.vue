<template>
	<Card
		:title="$t('transaction_history')"
		:subtitle="$t('your_past_transactions')"
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
				class="w-full"
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
				<div class="min-w-max lg:min-w-full">
					<div
						class="sticky top-0 grid grid-cols-7 items-center gap-x-8 border-b bg-white py-4 text-base text-gray-600 md:grid-cols-7"
					>
						<span class="font-bold">{{ $t('date') }}</span>
						<span class="font-bold">{{ $t('description') }}</span>
						<span class="text-right font-bold"
							>{{ $t('previous_balance') }} (VND)</span
						>
						<span class="text-right font-bold"
							>{{ $t('amount_of_money') }} (VND)</span
						>
						<span class="text-right font-bold">{{ $t('balance') }} (VND)</span>
						<span class="font-bold">{{ $t('status') }}</span>
						<span class="font-bold"></span>
					</div>
					<div v-if="!dataTrans" class="flex justify-center px-2 py-4">
						<LoadingText :text="$t('Loading') + '...'" />
					</div>
					<div v-else-if="dataTrans?.length">
						<details
							v-for="d in dataTrans"
							:key="d.name"
							class="cursor-pointer border-b"
						>
							<summary class="w-full focus:outline-none">
								<div
									class="grid grid-cols-7 items-center gap-x-8 py-4 text-base text-gray-900"
								>
									<div>
										<span :title="$t('view_details')">
											<subsummary></subsummary>
										</span>
										<span class="ml-2">
											{{ this.$formatDate(d.creation) }}
										</span>
									</div>
									<div class="text-gray-700">
										<div>
											{{ getDescription(d) }}
										</div>
									</div>
									<div class="text-right">
										{{ formatterMoney(d.pre.total_balance, 2) }}
									</div>
									<div class="text-right">
										{{ formatterMoney(d.total_amount, 2) }}
									</div>
									<div class="text-right">
										{{ formatterMoney(d.total_balance, 2) }}
									</div>
									<div class="whitespace-nowrap">
										<StatusOrder
											:status="getStatus(d)"
											:description="this.$getStatusDocTrans(getStatus(d))"
										></StatusOrder>
									</div>
									<div
										class="flex flex-wrap justify-end"
										v-if="
											d.docstatus == 0 &&
											d.payos_payment_status == 'PENDING' &&
											d.checkout_url
										"
									>
										<Link :href="d.checkout_url" class="mb-2 mr-2 border-none">
											<Button
												:variant="'solid'"
												theme="blue"
												size="sm"
												label="Button"
												:loading="false"
												:loadingText="null"
												:disabled="false"
												:link="null"
											>
												{{ $t('payment') }}
											</Button>
										</Link>
										<div class="mr-2">
											<Button
												:variant="'solid'"
												theme="red"
												size="sm"
												label="Button"
												@click="
													$resources.cancelOrder.submit({
														name: d.name,
														lang: this.$i18n.locale
													})
												"
												:loading="$resources.cancelOrder.loading"
											>
												{{ $t('cancel') }}
											</Button>
										</div>
									</div>
								</div>
							</summary>
							<div>
								<div class="overflow-auto rounded-md text-xs text-gray-900">
									<div class="w-full">
										<div
											class="grid grid-cols-7 gap-x-8 pb-4 text-base text-gray-900 md:grid-cols-7"
										>
											<!-- 1 -->
											<div></div>
											<div class="py-1 font-bold">
												{{ $t('deposit_amount') }}:
											</div>
											<div class="py-1 text-right">
												{{ formatterMoney(d.pre.balance, 2) }}
											</div>
											<div class="py-1 text-right">
												{{ formatterMoney(d.amount, 2) }}
											</div>
											<div class="py-1 text-right">
												{{ formatterMoney(d.ending_balance, 2) }}
											</div>
											<div></div>
											<div></div>

											<!-- 2 -->
											<div></div>
											<div class="py-1 font-bold">{{ $t('promotion_1') }}:</div>
											<div class="py-1 text-right">
												{{ formatterMoney(d.pre.promotion_balance_1, 2) }}
											</div>
											<div class="py-1 text-right">
												{{ formatterMoney(d.amount_promotion_1, 2) }}
											</div>
											<div class="py-1 text-right">
												{{ formatterMoney(d.promotion_balance_1, 2) }}
											</div>
											<div class="py-1">
												<Popover
													v-if="
														d.amount_promotion_1 > 0 || d.amount_promotion_2 > 0
													"
												>
													<template #target="{ togglePopover }">
														<span class="underline" @click="togglePopover()">
															{{ $t('Detail') }}
														</span>
													</template>
													<template #content>
														<div class="flex flex-col flex-wrap gap-2 p-2">
															<div
																v-if="d.amount_promotion_1"
																class="text-ink-gray-9 min-w-36 text-base"
															>
																{{ $t('AccountBillingCreditBalance_1') }}
																{{
																	d.promotion_expire
																		? formatterMoney(0, 2, 'VND')
																		: formatterMoney(
																				d.remaining_amount1,
																				2,
																				'VND'
																		  )
																}}
																{{ $t('AccountBillingCreditBalance_2') }}
																{{ d.date_promotion_expire }}.
															</div>
															<div
																v-if="d.amount_promotion_2 > 0"
																class="text-ink-gray-9 min-w-36 text-base"
															>
																{{ $t('AccountBillingCreditBalance_3') }}
																{{
																	formatterMoney(d.remaining_amount2, 2, 'VND')
																}}.
															</div>
														</div>
													</template>
												</Popover>
											</div>
											<div></div>

											<!-- 3 -->
											<div></div>
											<div class="py-1 font-bold">{{ $t('promotion_2') }}:</div>
											<div class="py-1 text-right">
												{{ formatterMoney(d.pre.promotion_balance_2, 2) }}
											</div>
											<div class="py-1 text-right">
												{{ formatterMoney(d.amount_promotion_2, 2) }}
											</div>
											<div class="py-1 text-right">
												{{ formatterMoney(d.promotion_balance_2, 2) }}
											</div>
											<div></div>
											<div></div>
										</div>
									</div>
								</div>
							</div>
						</details>
					</div>
					<div class="text-center text-base text-gray-600" v-else>
						<div class="px-2 py-4">
							{{ $t('no_results') }}
						</div>
					</div>
				</div>
			</div>
			<div class="flex flex-wrap items-center justify-end py-2">
				<Pagination
					v-if="dataTrans?.length"
					:options="optionsPagination"
					@updatePage="updatePage"
				/>
			</div>
		</div>
	</Card>
</template>
<script>
import { notify } from '@/utils/toast';
import { LoadingText } from 'frappe-ui';
import { watchDebounced } from '@vueuse/core';
import Pagination from '@/components/Table/Pagination.vue';
import ClearFilterIcon from '@/components/icons/ClearFilterIcon.vue';
import Popover from '@/components/Popover.vue';

export default {
	name: 'AccountBillingCreditBalance',
	components: {
		LoadingText,
		Pagination,
		ClearFilterIcon,
		Popover
	},
	data() {
		return {
			dataTrans: null,
			filters: this.setDefaultFilter(),
			optionsPagination: {
				currentPage: 1,
				totalPages: 0,
				pageSize: 20,
				total: 0
			},
			optionsStatus: [
				{ label: this.$t('All'), value: -1 },
				{ label: this.$getStatusDocTrans(0), value: 0 },
				{ label: this.$getStatusDocTrans(1), value: 1 },
				{ label: this.$getStatusDocTrans(2), value: 2 },
				{ label: this.$getStatusDocTrans(3), value: 3 }
			]
		};
	},
	mounted() {
		watchDebounced(
			() => ({ ...this.filters }),
			val => {
				this.dataTrans = null;
				this.getHistory();
			},
			{ debounce: 300, maxWait: 1000, deep: true, immediate: true }
		);
	},
	inject: ['viewportWidth'],
	resources: {
		balances() {
			return {
				url: 'press.api.billing.balances',
				onSuccess(data) {
					this.optionsPagination = {
						currentPage: data?.pagination?.page,
						totalPages: data?.pagination.total_page,
						pageSize: data?.pagination.page_length,
						total: data?.pagination.total
					};
					this.dataTrans = data?.result;
				}
			};
		},
		payosReturnCancelOrder() {
			var query = this.$route.query;
			if (
				query.id &&
				query.orderCode &&
				query.cancel == 'true' &&
				query.code == '00' &&
				query.status == 'CANCELLED'
			) {
				return {
					url: 'press.api.billing.payos_return_cancel_order',
					params: {
						order_code: query.orderCode,
						lang: this.$i18n.locale
					},
					auto: true,
					onSuccess(data) {
						this.$resources.balances.submit();
					}
				};
			}
		},
		cancelOrder() {
			return {
				url: 'press.api.billing.cancel_order',
				async onSuccess(data) {
					if (data.code == '00') {
						this.$resources.balances.submit();
					} else {
						notify({
							title: data.desc,
							color: 'red',
							icon: 'x'
						});
					}
				},
				onError(e) {
					notify({
						title: this.$t('an_error_occurred'),
						color: 'red',
						icon: 'x'
					});
				}
			};
		}
	},
	methods: {
		setDefaultFilter() {
			return {
				start_time: this.$startTimeOfMonth(),
				end_time: this.$endTimeOfMonth(),
				status: -1,
				page: 1
			};
		},
		clearFilter() {
			this.filters = this.setDefaultFilter();
		},
		getStatus(d) {
			var statusCode = 3;
			if (d.docstatus == 1) {
				statusCode = 1;
			} else if (d.docstatus == 2) {
				statusCode = 2;
			} else if (d.payos_payment_status == 'PENDING' && d.docstatus == 0) {
				statusCode = 0;
			}
			return statusCode;
		},
		getDescription(d) {
			if (d.type === 'Applied To Invoice' && d.formatted.invoice_for) {
				return `${this.$t('invoice_for')} ${d.formatted.invoice_for}`;
			}
			return this.$getTypeSource(d.source);
		},
		updatePage(page) {
			this.filters = {
				...this.filters,
				page: page
			};
		},
		getHistory() {
			this.$resources.balances.submit(this.filters);
		},
		formatterMoney(amount, decimal = 0, currency) {
			let formatM = '0';
			if (amount) {
				formatM = this.$formatMoney(amount, decimal);
			}
			if (currency) {
				formatM += ` ${currency}`;
			}
			return formatM;
		}
	}
};
</script>

<style scoped>
details summary {
	list-style-type: none;
}

details summary::-webkit-details-marker {
	display: none;
}

details subsummary::before {
	content: url("data:image/svg+xml,%3Csvg width='12' height='12' viewBox='0 0 12 12' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M4.25 9.5L7.75 6L4.25 2.5' stroke='%231F272E' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
}

details[open] subsummary::before {
	content: url("data:image/svg+xml,%3Csvg width='12' height='12' viewBox='0 0 12 12' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M2.5 4.25L6 7.75L9.5 4.25' stroke='%231F272E' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E%0A");
}
</style>
