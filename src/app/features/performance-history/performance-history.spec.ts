import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PerformanceHistory } from './performance-history';

describe('PerformanceHistory', () => {
  let component: PerformanceHistory;
  let fixture: ComponentFixture<PerformanceHistory>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PerformanceHistory],
    }).compileComponents();

    fixture = TestBed.createComponent(PerformanceHistory);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
